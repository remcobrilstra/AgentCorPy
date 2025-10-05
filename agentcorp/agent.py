from typing import List, Dict, Any, Optional
import json
from .providers import Provider, Message
from .memory import Memory
from .tasks import TaskManager
from . import tools as tools_module
from .tool_registry import ToolRegistry, ToolExecutionContext, global_tool_registry, Tool
from .logging import logger
from .models import ProviderResponse


class Agent:
    def __init__(self, provider: Provider, system_prompt: str = "", tool_names: Optional[List[str]] = None, context_settings: Optional[Dict[str, str]] = None):
        self.provider = provider
        provider_name = provider.__class__.__name__.replace('Provider', '').lower()
        self.memory = Memory(provider=provider_name, model=provider.model)
        self.task_manager = TaskManager()

        # Optional attributes
        self.name: Optional[str] = None
        self.description: Optional[str] = None

        # Create tool registry subset based on tool names
        if tool_names:
            self.tools = global_tool_registry.get_tools_by_names(tool_names)
        else:
            self.tools = {}  # Empty dict

        # Create execution context
        self.execution_context = ToolExecutionContext(
            settings=context_settings or {},
            agent_id=str(id(self)),
            session_id="",  # Can be set later if needed
            task_manager=self.task_manager
        )

        if system_prompt:
            self.memory.set_system_prompt(system_prompt)

    def chat(self, user_message: str, add_to_memory: bool = True, **kwargs) -> str:
        if add_to_memory:
            self.memory.add_message("user", user_message)

        if self.tools and self.provider.supports_tools():
            while True:
                tools_format = self.provider.get_tools_format(self.tools)
                response = self.provider.chat_with_tools(self.memory.get_messages(), tools_format, **kwargs)
                content = response.message
                tool_calls = response.function_calls
                input_tokens = response.input_tokens
                output_tokens = response.output_tokens

                if add_to_memory:
                    self.memory.add_response_message("assistant", response)

                if not tool_calls:
                    return content

                # Execute tool calls
                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]
                    tool = self.tools.get(tool_name)
                    if tool:
                        args = json.loads(tool_call["function"]["arguments"])
                        logger.log_tool_call(tool_name, args)
                        result = tool.execute(self.execution_context, **args)
                        logger.log_tool_call(tool_name, args, str(result)[:100] + "..." if len(str(result)) > 100 else str(result))
                    else:
                        result = None
                        logger.warning(f"Tool '{tool_name}' not found")
                    if add_to_memory:
                        self.memory.add_message("tool", str(result), tool_call_id=tool_call.get("id"))

        else:
            response = self.provider.chat(self.memory.get_messages(), **kwargs)
            content = response.message
            input_tokens = response.input_tokens
            output_tokens = response.output_tokens
            if add_to_memory:
                self.memory.add_response_message("assistant", response)
            return content

    def add_task(self, description: str) -> str:
        task_id = self.task_manager.add_task(description)
        logger.log_task_action("created", task_id, description)
        return task_id

    def get_tasks(self) -> Dict[str, Any]:
        return {
            "pending": [task.description for task in self.task_manager.get_pending_tasks()],
            "in_progress": [task.description for task in self.task_manager.get_in_progress_tasks()],
            "completed": [task.description for task in self.task_manager.get_completed_tasks()]
        }

    def update_task(self, task_id: str, status: str, result: Any = None, error: str = None):
        from .tasks import TaskStatus
        status_enum = TaskStatus(status.lower())
        self.task_manager.update_task_status(task_id, status_enum, result, error)
        logger.log_task_action(f"status_changed_to_{status.lower()}", task_id, f"Status: {status}", result=result, error=error)

    def add_complex_task(self, description: str, subtasks: List[str]) -> str:
        """Add a complex task that will be decomposed into subtasks"""
        task_id = self.task_manager.add_complex_task(description, subtasks)
        logger.log_task_action("created_complex", task_id, description, subtasks_count=len(subtasks))
        return task_id

    def decompose_task(self, task_description: str) -> str:
        """Use the LLM to decompose a complex task into subtasks"""
        prompt = f"""
        Break down the following complex task into smaller, sequential, manageable subtasks.
        Keep the amount of subtasks reasonable (5-10), and ensure they are actionable.
        Make the descriptions short and concise.
        You can always iterate on the subtasks later if needed, keep the list as short as possible to achieve the goal.
        Provide the subtasks as a numbered list.

        Task: {task_description}

        Subtasks:
        """

        #self.memory.add_message("system", "You are a task decomposition expert. Break down complex tasks into logical, sequential steps.")
        msg = self.memory.add_message("user", prompt)

        response_raw = self.provider.chat(self.memory.get_messages())
        response = response_raw.message
        #self.memory.add_message("assistant", response)
        self.memory.remove_message(msg)

        # Parse the response to extract subtasks
        lines = response.strip().split('\n')
        subtasks = []
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering
                if line[0].isdigit():
                    line = line.split('.', 1)[-1].strip()
                elif line.startswith('-'):
                    line = line[1:].strip()
                if line:
                    subtasks.append(line)

        if subtasks:
            logger.info(f"Decomposed task into {len(subtasks)} subtasks")
            logger.debug("Subtasks:")
            for i, subtask in enumerate(subtasks, 1):
                logger.debug(f"  {i}. {subtask}")

            return self.add_complex_task(task_description, subtasks)
        else:
            # Fallback: create a single task
            return self.add_task(task_description)

    def execute_task_sequentially(self, task_id: str) -> Any:
        """Execute a task and its subtasks sequentially"""
        logger.log_task_action("execution_started", task_id, "Starting sequential execution")
        result = self.task_manager.execute_task_sequentially(self, task_id)
        logger.log_task_action("execution_completed", task_id, "Sequential execution finished", result=str(result)[:100] + "..." if len(str(result)) > 100 else str(result))
        return result

    def handle_complex_query(self, query: str) -> str:
        """Handle a complex query by decomposing it into tasks and executing them"""
        # First, determine if this is a complex task
        complexity_prompt = f"""
        Analyze the following query and determine if it requires multiple steps or can be handled as a single task.

        Query: {query}

        Is this a complex task that should be broken down? Answer with YES or NO, then briefly explain why.
        """

        msg1 = self.memory.add_message("user", complexity_prompt)
        complexity_response = self.provider.chat(self.memory.get_messages())
        content = complexity_response.message
        msg2 = self.memory.add_response_message("assistant", complexity_response)

        self.memory.remove_message(msg1)
        self.memory.remove_message(msg2)

        if "YES" in content.upper():
            # Decompose and execute
            task_id = self.decompose_task(query)
            result = self.execute_task_sequentially(task_id)

            # Generate final response based on task completion
            final_response = f"Complex task completed. Results: {result}"
            self.memory.add_message("assistant", final_response)
            return final_response
        else:
            # Handle as simple query
            return self.chat(query)