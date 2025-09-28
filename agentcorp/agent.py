from typing import List, Dict, Any, Optional
from .providers import Provider, Message
from .memory import Memory
from .tasks import TaskManager
from . import tools as tools_module
from .tool_registry import ToolRegistry, ToolExecutionContext, global_tool_registry


class Agent:
    def __init__(self, provider: Provider, system_prompt: str = "", tool_names: Optional[List[str]] = None, context_settings: Optional[Dict[str, str]] = None):
        self.provider = provider
        self.memory = Memory()
        self.task_manager = TaskManager()

        # Optional attributes
        self.name: Optional[str] = None
        self.description: Optional[str] = None

        # Create tool registry subset based on tool names
        if tool_names:
            self.tools = global_tool_registry.get_tools_by_names(tool_names)
        else:
            self.tools = ToolRegistry()  # Empty registry

        # Create execution context
        self.execution_context = ToolExecutionContext(
            settings=context_settings or {},
            agent_id=str(id(self)),
            session_id="",  # Can be set later if needed
        )

        if system_prompt:
            self.memory.set_system_prompt(system_prompt)

    def chat(self, user_message: str, **kwargs) -> str:
        self.memory.add_message("user", user_message)

        if self.tools.tools and self.provider.supports_tools():
            tools_format = self.tools.get_tools_for_provider(self.provider.__class__.__name__.replace("Provider", "").lower())
            response = self.provider.chat_with_tools(self.memory.get_messages(), tools_format, **kwargs)
            content = response.get("content", "")
            tool_calls = response.get("tool_calls", [])

            # Execute tool calls
            for tool_call in tool_calls:
                result = self.tools.execute_tool(tool_call, self.execution_context)
                self.memory.add_message("assistant", f"Tool call: {tool_call}")
                self.memory.add_message("tool", str(result))

            # If there are tool calls, get final response
            if tool_calls:
                final_response = self.provider.chat(self.memory.get_messages(), **kwargs)
                self.memory.add_message("assistant", final_response)
                return final_response
            else:
                self.memory.add_message("assistant", content)
                return content
        else:
            response = self.provider.chat(self.memory.get_messages(), **kwargs)
            self.memory.add_message("assistant", response)
            return response

    def add_task(self, description: str) -> str:
        return self.task_manager.add_task(description)

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

    def add_complex_task(self, description: str, subtasks: List[str]) -> str:
        """Add a complex task that will be decomposed into subtasks"""
        return self.task_manager.add_complex_task(description, subtasks)

    def decompose_task(self, task_description: str) -> str:
        """Use the LLM to decompose a complex task into subtasks"""
        prompt = f"""
        Break down the following complex task into smaller, manageable subtasks.
        Provide the subtasks as a numbered list.

        Task: {task_description}

        Subtasks:
        """

        self.memory.add_message("system", "You are a task decomposition expert. Break down complex tasks into logical, sequential steps.")
        self.memory.add_message("user", prompt)

        response = self.provider.chat(self.memory.get_messages())
        self.memory.add_message("assistant", response)

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
            return self.add_complex_task(task_description, subtasks)
        else:
            # Fallback: create a single task
            return self.add_task(task_description)

    def execute_task_sequentially(self, task_id: str) -> Any:
        """Execute a task and its subtasks sequentially"""
        return self.task_manager.execute_task_sequentially(self, task_id)

    def handle_complex_query(self, query: str) -> str:
        """Handle a complex query by decomposing it into tasks and executing them"""
        # First, determine if this is a complex task
        complexity_prompt = f"""
        Analyze the following query and determine if it requires multiple steps or can be handled as a single task.

        Query: {query}

        Is this a complex task that should be broken down? Answer with YES or NO, then briefly explain why.
        """

        self.memory.add_message("user", complexity_prompt)
        complexity_response = self.provider.chat(self.memory.get_messages())
        self.memory.add_message("assistant", complexity_response)

        if "YES" in complexity_response.upper():
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