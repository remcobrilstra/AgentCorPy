"""
Replace in file tool for the AgentCorp framework
"""

from ...tool_registry import Tool, global_tool_registry, ToolExecutionContext
from .utils import _validate_path
from ...logging import logger

def replace_in_file(context: ToolExecutionContext, file_path: str, old_text: str, new_text: str, encoding: str = "utf-8", count: int = -1) -> str:
    """
    Replace text in a file.

    Args:
        context: Tool execution context
        file_path: Path to the file to modify
        old_text: Text to search for
        new_text: Text to replace with
        encoding: File encoding (default: utf-8)
        count: Maximum number of replacements (default: -1 for all occurrences)

    Returns:
        str: Success message with replacement count or error message
    """
    is_valid, error_msg, resolved_path = _validate_path(context, file_path)
    if not is_valid:
        return error_msg

    try:
        logger.info(f"Replacing text in file [{file_path}]")
        if not resolved_path.exists():
            return f"Error: File {file_path} does not exist"

        if not resolved_path.is_file():
            return f"Error: {file_path} is not a file"

        # Read the file
        with open(resolved_path, 'r', encoding=encoding) as f:
            content = f.read()

        # Perform replacement
        if count == -1:
            new_content = content.replace(old_text, new_text)
            replacements = content.count(old_text)
        else:
            new_content = content.replace(old_text, new_text, count)
            replacements = min(content.count(old_text), count)

        # Write back to file
        with open(resolved_path, 'w', encoding=encoding) as f:
            f.write(new_content)

        return f"Successfully replaced {replacements} occurrence(s) of '{old_text}' with '{new_text}' in {file_path}"

    except UnicodeDecodeError:
        return f"Error: Could not decode file {file_path} with encoding {encoding}"
    except PermissionError:
        return f"Error: Permission denied modifying file {file_path}"
    except Exception as e:
        return f"Error replacing text in file {file_path}: {e}"


# Create the replace_in_file tool
replace_in_file_tool = Tool(
    name="filesys.replace_in_file",
    description="Replace text in a file. Operations are restricted to the working directory if set in context.",
    function=replace_in_file,
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to modify"
            },
            "old_text": {
                "type": "string",
                "description": "Text to search for and replace"
            },
            "new_text": {
                "type": "string",
                "description": "Text to replace with"
            },
            "encoding": {
                "type": "string",
                "description": "File encoding (default: utf-8)",
                "default": "utf-8"
            },
            "count": {
                "type": "integer",
                "description": "Maximum number of replacements (-1 for all occurrences, default: -1)",
                "default": -1
            }
        },
        "required": ["file_path", "old_text", "new_text"]
    }
)

# Register the tool
global_tool_registry.register_tool(replace_in_file_tool)