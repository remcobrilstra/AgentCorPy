"""
Write file tool for the AgentCorp framework
"""

from ...tool_registry import Tool, global_tool_registry, ToolExecutionContext
from .utils import _validate_path


def write_file(context: ToolExecutionContext, file_path: str, content: str, encoding: str = "utf-8", create_dirs: bool = True) -> str:
    """
    Write content to a file.

    Args:
        context: Tool execution context
        file_path: Path to the file to write
        content: Content to write to the file
        encoding: File encoding (default: utf-8)
        create_dirs: Whether to create parent directories if they don't exist (default: True)

    Returns:
        str: Success message or error message
    """
    is_valid, error_msg, resolved_path = _validate_path(context, file_path)
    if not is_valid:
        return error_msg

    try:
        # Create parent directories if requested
        if create_dirs:
            resolved_path.parent.mkdir(parents=True, exist_ok=True)

        with open(resolved_path, 'w', encoding=encoding) as f:
            f.write(content)

        return f"Successfully wrote {len(content)} characters to {file_path}"

    except PermissionError:
        return f"Error: Permission denied writing to file {file_path}"
    except Exception as e:
        return f"Error writing to file {file_path}: {e}"


# Create the write_file tool
write_file_tool = Tool(
    name="write_file",
    description="Write content to a file. Creates parent directories if needed. Operations are restricted to the working directory if set in context.",
    function=write_file,
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to write"
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file"
            },
            "encoding": {
                "type": "string",
                "description": "File encoding (default: utf-8)",
                "default": "utf-8"
            },
            "create_dirs": {
                "type": "boolean",
                "description": "Whether to create parent directories if they don't exist (default: true)",
                "default": True
            }
        },
        "required": ["file_path", "content"]
    }
)

# Register the tool
global_tool_registry.register_tool(write_file_tool)