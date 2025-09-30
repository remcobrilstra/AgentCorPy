"""
Add subtask tool for the AgentCorp framework
"""

from ...tool_registry import Tool, global_tool_registry, ToolExecutionContext


def add_subtask(context: ToolExecutionContext, description: str, parent_task_id: str = None) -> str:
    """
    Add a subtask to an existing task.

    Args:
        context: Tool execution context
        description: Description of the subtask to add
        parent_task_id: ID of the parent task (optional, uses current_task_id from context if not provided)

    Returns:
        str: Confirmation message
    """
    if not hasattr(context, 'task_manager'):
        return "Error: Task manager not available in context"

    # Use parent_task_id if provided, otherwise check context for current_task_id
    task_id = parent_task_id
    if not task_id and hasattr(context, 'current_task_id'):
        task_id = context.current_task_id

    if not task_id:
        return "Error: No parent task ID provided and no current task set in context"

    try:
        parent_task = context.task_manager.get_task(task_id)
        if not parent_task:
            return f"Error: Parent task with ID {task_id} not found"

        subtask = parent_task.add_subtask(description)
        return f"Subtask added successfully with ID: {subtask.id}"
    except Exception as e:
        return f"Error adding subtask: {e}"


# Create the add_subtask tool
add_subtask_tool = Tool(
    name="task.add_subtask",
    description="Add a subtask to an existing task in the agent's task manager. Uses current task from context if no parent_task_id provided.",
    function=add_subtask,
    parameters={
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": "Description of the subtask to add"
            },
            "parent_task_id": {
                "type": "string",
                "description": "ID of the parent task to add the subtask to (optional, uses current task from context)"
            }
        },
        "required": ["description"]
    }
)

# Register the tool
global_tool_registry.register_tool(add_subtask_tool)