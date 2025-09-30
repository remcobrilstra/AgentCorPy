"""
Read file tool for the AgentCorp framework
"""

from ...tool_registry import Tool, global_tool_registry, ToolExecutionContext
from .utils import _validate_path
from ...logging import logger

def read_file(context: ToolExecutionContext, file_path: str, encoding: str = "utf-8") -> str:
    """
    Read the contents of a file.

    Args:
        context: Tool execution context
        file_path: Path to the file to read
        encoding: File encoding (default: utf-8)

    Returns:
        str: File contents or error message
    """
    is_valid, error_msg, resolved_path = _validate_path(context, file_path)
    if not is_valid:
        return error_msg

    try:
        logger.info(f"Reading file [{file_path}]")
        if not resolved_path.exists():
            return f"Error: File {file_path} does not exist"

        if not resolved_path.is_file():
            return f"Error: {file_path} is not a file"

        with open(resolved_path, 'r', encoding=encoding) as f:
            content = f.read()

        return content

    except UnicodeDecodeError:
        return f"Error: Could not decode file {file_path} with encoding {encoding}"
    except PermissionError:
        return f"Error: Permission denied reading file {file_path}"
    except Exception as e:
        return f"Error reading file {file_path}: {e}"


# Create the read_file tool
read_file_tool = Tool(
    name="filesys.read_file",
    description="Read the contents of a file. Operations are restricted to the working directory if set in context.",
    function=read_file,
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to read"
            },
            "encoding": {
                "type": "string",
                "description": "File encoding (default: utf-8)",
                "default": "utf-8"
            }
        },
        "required": ["file_path"]
    }
)

# Register the tool
global_tool_registry.register_tool(read_file_tool)