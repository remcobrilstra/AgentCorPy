from typing import List, Dict, Any, Callable, Optional, TYPE_CHECKING
from enum import Enum
from .logging import logger

if TYPE_CHECKING:
    from .agent import Agent


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Task:
    def __init__(self, description: str, task_id: str = None, parent_task: Optional['Task'] = None):
        self.id = task_id or str(id(self))
        self.description = description
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.parent_task = parent_task
        self.subtasks: List['Task'] = []

    def add_subtask(self, description: str) -> 'Task':
        subtask = Task(description, parent_task=self)
        self.subtasks.append(subtask)
        return subtask

    def start(self):
        self.status = TaskStatus.IN_PROGRESS

    def complete(self, result: Any = None):
        self.status = TaskStatus.COMPLETED
        self.result = result
        # If this is a subtask, check if parent can be completed
        if self.parent_task:
            self.parent_task._check_completion()

    def fail(self, error: str):
        self.status = TaskStatus.FAILED
        self.error = error

    def _check_completion(self):
        """Check if all subtasks are completed"""
        if all(subtask.status == TaskStatus.COMPLETED for subtask in self.subtasks):
            self.complete()

    def execute(self, agent: 'Agent', overall_task: Optional['Task'] = None, previous_results: Optional[List[Dict[str, Any]]] = None) -> Any:
        """Execute the task using the provided agent with LLM and tools"""
        if overall_task is None:
            overall_task = self
        if previous_results is None:
            previous_results = []

        logger.log_task_action("execution_started", self.id, self.description)

        overall_desc = overall_task.description
        previous_str = "\n".join(f"- {pr['description']}: {pr['result']}" for pr in previous_results) if previous_results else "None"

        prompt = f"""You are working on the following overall task: {overall_desc}

Previous steps completed:
{previous_str}

Current task to complete: {self.description}

Use your available tools and knowledge to complete this task. Provide the result or confirmation when done."""

        logger.info(f"Executing Task {self.id}: {self.description}")
        result = agent.chat(prompt, add_to_memory=True)
        logger.info(f"Completed Task {self.id}: {self.description}")
        logger.info(f"Cost: {agent.memory.get_total_cost()} | Tokens Used: {agent.memory.get_total_tokens_used()}")
        logger.log_task_action("execution_completed", self.id, self.description, result=str(result)[:100] + "..." if len(str(result)) > 100 else str(result))
        return result

    def get_all_subtasks(self) -> List['Task']:
        """Get all subtasks recursively"""
        all_subtasks = []
        for subtask in self.subtasks:
            all_subtasks.append(subtask)
            all_subtasks.extend(subtask.get_all_subtasks())
        return all_subtasks

    def is_complex(self) -> bool:
        """Check if this is a complex task (has subtasks)"""
        return len(self.subtasks) > 0


class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def add_task(self, description: str) -> str:
        task = Task(description)
        self.tasks[task.id] = task
        logger.log_task_action("added", task.id, description)
        return task.id

    def add_complex_task(self, description: str, subtasks: List[str]) -> str:
        """Add a complex task with subtasks"""
        task = Task(description)
        for sub_desc in subtasks:
            task.add_subtask(sub_desc)
        self.tasks[task.id] = task
        logger.log_task_action("added_complex", task.id, description, subtasks_count=len(subtasks))
        return task.id

    def get_task(self, task_id: str) -> Task:
        return self.tasks.get(task_id)

    def update_task_status(self, task_id: str, status: TaskStatus, result: Any = None, error: str = None):
        task = self.tasks.get(task_id)
        if task:
            task.status = status
            if status == TaskStatus.COMPLETED:
                task.result = result
            elif status == TaskStatus.FAILED:
                task.error = error
            logger.log_task_action(f"status_changed_to_{status.value}", task_id, task.description, result=result, error=error)

    def get_pending_tasks(self) -> List[Task]:
        return [task for task in self.tasks.values() if task.status == TaskStatus.PENDING]

    def get_in_progress_tasks(self) -> List[Task]:
        return [task for task in self.tasks.values() if task.status == TaskStatus.IN_PROGRESS]

    def get_completed_tasks(self) -> List[Task]:
        return [task for task in self.tasks.values() if task.status == TaskStatus.COMPLETED]

    def execute_task_sequentially(self, agent: 'Agent', task_id: str) -> Any:
        """Execute a task and its subtasks sequentially"""
        task = self.get_task(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return None

        logger.log_task_action("sequential_execution_started", task_id, task.description)

        # If it's a complex task, execute subtasks first
        if task.is_complex():
            for i, subtask in enumerate(task.subtasks):
                if subtask.status == TaskStatus.PENDING:
                    logger.log_task_action("subtask_started", subtask.id, subtask.description, parent_task=task_id)
                    subtask.start()
                    # Build previous results from completed subtasks before this one
                    previous_results = [
                        {"description": task.subtasks[j].description, "result": task.subtasks[j].result}
                        for j in range(i) if task.subtasks[j].status == TaskStatus.COMPLETED
                    ]
                    result = subtask.execute(agent, overall_task=task, previous_results=previous_results)
                    subtask.complete(result)
                    logger.log_task_action("subtask_completed", subtask.id, subtask.description, result=str(result)[:50] + "..." if len(str(result)) > 50 else str(result))

            # After all subtasks are done, execute the main task
            logger.log_task_action("main_task_started", task_id, task.description)
            task.start()
            # Previous results are all subtasks
            previous_results = [
                {"description": st.description, "result": st.result}
                for st in task.subtasks if st.status == TaskStatus.COMPLETED
            ]
            result = task.execute(agent, overall_task=task, previous_results=previous_results)
            task.complete(result)
            logger.log_task_action("sequential_execution_completed", task_id, task.description, result=str(result)[:100] + "..." if len(str(result)) > 100 else str(result))
            return result
        else:
            # Simple task execution
            logger.log_task_action("simple_task_started", task_id, task.description)
            task.start()
            result = task.execute(agent, overall_task=task, previous_results=[])
            task.complete(result)
            logger.log_task_action("simple_task_completed", task_id, task.description, result=str(result)[:100] + "..." if len(str(result)) > 100 else str(result))
            return result