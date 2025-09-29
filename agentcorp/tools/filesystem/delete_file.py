"""
Delete file tool for the AgentCorp framework
"""

from ...tool_registry import Tool, global_tool_registry, ToolExecutionContext
from .utils import _validate_path


def delete_file(context: ToolExecutionContext, file_path: str) -> str:
    """
    Delete a file.

    Args:
        context: Tool execution context
        file_path: Path to the file to delete

    Returns:
        str: Success message or error message
    """
    is_valid, error_msg, resolved_path = _validate_path(context, file_path)
    if not is_valid:
        return error_msg

    try:
        if not resolved_path.exists():
            return f"Error: File {file_path} does not exist"

        if not resolved_path.is_file():
            return f"Error: {file_path} is not a file (use a directory deletion tool for directories)"

        resolved_path.unlink()
        return f"Successfully deleted file {file_path}"

    except PermissionError:
        return f"Error: Permission denied deleting file {file_path}"
    except Exception as e:
        return f"Error deleting file {file_path}: {e}"


# Create the delete_file tool
delete_file_tool = Tool(
    name="filesys.delete_file",
    description="Delete a file. Operations are restricted to the working directory if set in context.",
    function=delete_file,
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to delete"
            }
        },
        "required": ["file_path"]
    }
)

# Register the tool
global_tool_registry.register_tool(delete_file_tool)