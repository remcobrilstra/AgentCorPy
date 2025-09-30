"""
Update task status tool for the AgentCorp framework
"""

from ...tool_registry import Tool, global_tool_registry, ToolExecutionContext
from ...tasks import TaskStatus


def update_task_status(context: ToolExecutionContext, task_id: str, status: str, result: str = None, error: str = None) -> str:
    """
    Update the status of an existing task.

    Args:
        context: Tool execution context
        task_id: ID of the task to update
        status: New status (pending, in_progress, completed, failed)
        result: Result if status is completed
        error: Error message if status is failed

    Returns:
        str: Confirmation message
    """
    if not hasattr(context, 'task_manager'):
        return "Error: Task manager not available in context"

    try:
        # Validate status
        valid_statuses = [s.value for s in TaskStatus]
        if status not in valid_statuses:
            return f"Error: Invalid status '{status}'. Valid statuses: {', '.join(valid_statuses)}"

        status_enum = TaskStatus(status)
        context.task_manager.update_task_status(task_id, status_enum, result, error)
        return f"Task {task_id} status updated to {status}"
    except Exception as e:
        return f"Error updating task status: {e}"


# Create the update_task_status tool
update_task_status_tool = Tool(
    name="task.update_task_status",
    description="Update the status of an existing task in the agent's task manager.",
    function=update_task_status,
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "ID of the task to update"
            },
            "status": {
                "type": "string",
                "description": "New status for the task",
                "enum": ["pending", "in_progress", "completed", "failed"]
            },
            "result": {
                "type": "string",
                "description": "Result of the task (required if status is completed)"
            },
            "error": {
                "type": "string",
                "description": "Error message (required if status is failed)"
            }
        },
        "required": ["task_id", "status"]
    }
)

# Register the tool
global_tool_registry.register_tool(update_task_status_tool)