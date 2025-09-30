"""
Create task tool for the AgentCorp framework
"""

from ...tool_registry import Tool, global_tool_registry, ToolExecutionContext


def create_task(context: ToolExecutionContext, description: str) -> str:
    """
    Create a new task in the agent's task manager.

    Args:
        context: Tool execution context
        description: Description of the task to create

    Returns:
        str: Task ID of the created task
    """
    if not hasattr(context, 'task_manager'):
        return "Error: Task manager not available in context"

    try:
        task_id = context.task_manager.add_task(description)
        return f"Task created successfully with ID: {task_id}"
    except Exception as e:
        return f"Error creating task: {e}"


# Create the create_task tool
create_task_tool = Tool(
    name="task.create_task",
    description="Create a new task in the agent's task manager.",
    function=create_task,
    parameters={
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": "Description of the task to create"
            }
        },
        "required": ["description"]
    }
)

# Register the tool
global_tool_registry.register_tool(create_task_tool)