from typing import List, Dict, Any, Callable, Optional, TYPE_CHECKING
from enum import Enum

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
        self.execution_function: Optional[Callable] = None

    def add_subtask(self, description: str) -> 'Task':
        subtask = Task(description, parent_task=self)
        self.subtasks.append(subtask)
        return subtask

    def set_execution_function(self, func: Callable):
        self.execution_function = func

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

    def execute(self, agent: 'Agent') -> Any:
        """Execute the task using the provided agent"""
        if self.execution_function:
            return self.execution_function(agent, self)
        return None

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
        return task.id

    def add_complex_task(self, description: str, subtasks: List[str]) -> str:
        """Add a complex task with subtasks"""
        task = Task(description)
        for sub_desc in subtasks:
            task.add_subtask(sub_desc)
        self.tasks[task.id] = task
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
            return None

        # If it's a complex task, execute subtasks first
        if task.is_complex():
            for subtask in task.subtasks:
                if subtask.status == TaskStatus.PENDING:
                    subtask.start()
                    result = subtask.execute(agent)
                    if result is not None:
                        subtask.complete(result)
                    else:
                        # If execution function returns None, assume it was handled internally
                        subtask.complete()

            # After all subtasks are done, execute the main task
            task.start()
            result = task.execute(agent)
            task.complete(result)
            return result
        else:
            # Simple task execution
            task.start()
            result = task.execute(agent)
            task.complete(result)
            return result