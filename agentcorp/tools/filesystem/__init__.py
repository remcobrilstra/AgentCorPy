"""
Filesystem tools for the AgentCorp framework

These tools provide secure file operations with working directory restrictions.
All operations are restricted to the 'workingdir' setting if specified in the context.
"""

import os
from pathlib import Path
from typing import Optional

from ...tool_registry import Tool, global_tool_registry, ToolExecutionContext


def _validate_path(context: ToolExecutionContext, file_path: str) -> tuple[bool, str, Path]:
    """
    Validate that the file path is within the allowed working directory.
    
    Args:
        context: Tool execution context
        file_path: The file path to validate
        
    Returns:
        tuple: (is_valid, error_message, resolved_path)
    """
    workingdir = context.get_setting("workingdir", "")
    
    if not workingdir:
        # No restriction set, allow any path but still resolve it
        try:
            resolved_path = Path(file_path).resolve()
            return True, "", resolved_path
        except Exception as e:
            return False, f"Error resolving path: {e}", Path()
    
    try:
        # Resolve both paths to prevent directory traversal attacks
        working_dir_path = Path(workingdir).resolve()
        
        # If file_path is relative, resolve it relative to the working directory
        if Path(file_path).is_absolute():
            file_full_path = Path(file_path).resolve()
        else:
            file_full_path = (working_dir_path / file_path).resolve()
        
        # Check if the file path is within the working directory
        if not str(file_full_path).startswith(str(working_dir_path)):
            return False, f"Access denied: {file_path} is outside the allowed working directory {workingdir}", Path()
        
        return True, "", file_full_path
        
    except Exception as e:
        return False, f"Error validating path: {e}", Path()


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


def file_search(context: ToolExecutionContext, query: str, max_results: int = 20) -> str:
    """
    Search for files in the workspace by glob pattern.
    
    Args:
        context: Tool execution context
        query: Glob pattern to search for files
        max_results: Maximum number of results to return (default: 20)
        
    Returns:
        str: List of matching file paths or error message
    """
    import glob
    from pathlib import Path
    
    workingdir = context.get_setting("workingdir", "")
    
    # Determine the search root
    if workingdir:
        try:
            search_root = Path(workingdir).resolve()
        except Exception as e:
            return f"Error resolving working directory: {e}"
    else:
        # If no working directory is set, use current directory
        search_root = Path.cwd()
    
    try:
        # Ensure the query doesn't try to escape the working directory
        if ".." in query or query.startswith("/") or query.startswith("\\"):
            if workingdir:
                return f"Error: Search pattern cannot contain '..' or absolute paths when working directory is restricted"
        
        # Convert to absolute glob pattern
        if workingdir:
            # Make the glob pattern relative to working directory
            search_pattern = str(search_root / query)
        else:
            search_pattern = query
        
        # Perform the glob search
        matches = glob.glob(search_pattern, recursive=True)
        
        # Filter out directories, keep only files
        file_matches = []
        for match in matches:
            match_path = Path(match)
            if match_path.is_file():
                # If working directory is set, show paths relative to it
                if workingdir:
                    try:
                        relative_path = match_path.relative_to(search_root)
                        file_matches.append(str(relative_path))
                    except ValueError:
                        # File is outside working directory, skip it
                        continue
                else:
                    file_matches.append(str(match_path))
        
        # Limit results
        if len(file_matches) > max_results:
            file_matches = file_matches[:max_results]
            truncated_msg = f" (showing first {max_results} of {len(glob.glob(search_pattern, recursive=True))} matches)"
        else:
            truncated_msg = ""
        
        if not file_matches:
            return f"No files found matching pattern: {query}"
        
        # Format the results
        results = "\n".join(f"  - {path}" for path in sorted(file_matches))
        return f"Found {len(file_matches)} file(s) matching '{query}':{truncated_msg}\n{results}"
        
    except Exception as e:
        return f"Error searching for files with pattern '{query}': {e}"


def grep_search(context: ToolExecutionContext, query: str, include_pattern: str = "**/*", is_regexp: bool = False, max_results: int = 20) -> str:
    """
    Search for text patterns within files using grep-like functionality.
    
    Args:
        context: Tool execution context
        query: Text pattern to search for (plain text or regex)
        include_pattern: Glob pattern for files to search in (default: "**/*")
        is_regexp: Whether the query is a regular expression (default: False)
        max_results: Maximum number of results to return (default: 20)
        
    Returns:
        str: Search results with file paths, line numbers, and matching lines
    """
    import re
    import glob
    from pathlib import Path
    
    workingdir = context.get_setting("workingdir", "")
    
    # Determine the search root
    if workingdir:
        try:
            search_root = Path(workingdir).resolve()
        except Exception as e:
            return f"Error resolving working directory: {e}"
    else:
        # If no working directory is set, use current directory
        search_root = Path.cwd()
    
    try:
        # Validate include pattern for security
        if ".." in include_pattern or include_pattern.startswith("/") or include_pattern.startswith("\\"):
            if workingdir:
                return f"Error: Include pattern cannot contain '..' or absolute paths when working directory is restricted"
        
        # Convert include pattern to absolute
        if workingdir:
            search_pattern = str(search_root / include_pattern)
        else:
            search_pattern = include_pattern
        
        # Get all matching files
        file_matches = []
        for match in glob.glob(search_pattern, recursive=True):
            match_path = Path(match)
            if match_path.is_file():
                # If working directory is set, check if file is within it
                if workingdir:
                    try:
                        match_path.relative_to(search_root)
                        file_matches.append(match_path)
                    except ValueError:
                        # File is outside working directory, skip it
                        continue
                else:
                    file_matches.append(match_path)
        
        if not file_matches:
            return f"No files found matching pattern: {include_pattern}"
        
        # Compile regex if needed
        if is_regexp:
            try:
                pattern = re.compile(query, re.MULTILINE | re.IGNORECASE)
            except re.error as e:
                return f"Invalid regular expression '{query}': {e}"
        else:
            # Escape special regex characters for plain text search
            escaped_query = re.escape(query)
            pattern = re.compile(escaped_query, re.MULTILINE | re.IGNORECASE)
        
        # Search through files
        results = []
        total_matches = 0
        
        for file_path in file_matches:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Find all matches with line numbers
                lines = content.splitlines()
                file_matches_found = []
                
                for line_num, line in enumerate(lines, 1):
                    if pattern.search(line):
                        file_matches_found.append((line_num, line.strip()))
                        total_matches += 1
                        
                        # Limit results per file to prevent overwhelming output
                        if len(file_matches_found) >= 10:  # Max 10 matches per file
                            break
                
                if file_matches_found:
                    # Show relative path if working directory is set
                    if workingdir:
                        display_path = file_path.relative_to(search_root)
                    else:
                        display_path = file_path
                    
                    results.append(f"File: {display_path}")
                    for line_num, line_content in file_matches_found:
                        # Truncate long lines
                        if len(line_content) > 100:
                            line_content = line_content[:97] + "..."
                        results.append(f"  {line_num}: {line_content}")
                    results.append("")  # Empty line between files
                    
                    # Limit total results
                    if len(results) >= max_results * 2:  # Rough estimate
                        break
                        
            except (UnicodeDecodeError, PermissionError, OSError):
                # Skip files that can't be read
                continue
        
        if not results:
            return f"No matches found for '{query}' in files matching '{include_pattern}'"
        
        # Format final output
        if total_matches > max_results:
            results.insert(0, f"Found {total_matches} matches (showing first {max_results}):")
            results = results[:max_results + 1]  # +1 for the header
        else:
            results.insert(0, f"Found {total_matches} matches:")
        
        return "\n".join(results)
        
    except Exception as e:
        return f"Error searching for pattern '{query}': {e}"


# Create the filesystem tools
read_file_tool = Tool(
    name="read_file",
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

replace_in_file_tool = Tool(
    name="replace_in_file",
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

delete_file_tool = Tool(
    name="delete_file",
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

file_search_tool = Tool(
    name="file_search",
    description="Search for files in the workspace by glob pattern. This only returns the paths of matching files. Limited to 20 results. Use this tool when you know the exact filename pattern of the files you're searching for. Glob patterns match from the root of the workspace folder. Examples:\n- **/*.{js,ts} to match all js/ts files in the workspace.\n- src/** to match all files under the top-level src folder.\n- **/foo/**/*.js to match all js files under any foo folder in the workspace.",
    function=file_search,
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search for files with names or paths matching this query. Can be a glob pattern."
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 20)",
                "default": 20
            }
        },
        "required": ["query"]
    }
)

grep_search_tool = Tool(
    name="grep_search",
    description="Search for text patterns within files using grep-like functionality. Supports both plain text and regular expressions. Results include file paths, line numbers, and matching lines.",
    function=grep_search,
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Text pattern to search for (plain text or regex)"
            },
            "include_pattern": {
                "type": "string",
                "description": "Glob pattern for files to search in (default: '**/*')",
                "default": "**/*"
            },
            "is_regexp": {
                "type": "boolean",
                "description": "Whether the query is a regular expression (default: false)",
                "default": False
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 20)",
                "default": 20
            }
        },
        "required": ["query"]
    }
)

# Register all filesystem tools
global_tool_registry.register_tool(read_file_tool)
global_tool_registry.register_tool(write_file_tool)
global_tool_registry.register_tool(replace_in_file_tool)
global_tool_registry.register_tool(delete_file_tool)
global_tool_registry.register_tool(file_search_tool)
global_tool_registry.register_tool(grep_search_tool)