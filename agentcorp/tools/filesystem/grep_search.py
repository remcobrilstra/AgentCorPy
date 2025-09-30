"""
Grep search tool for the AgentCorp framework
"""

import re
import glob
from pathlib import Path
from ...logging import logger

from ...tool_registry import Tool, global_tool_registry, ToolExecutionContext


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
        logger.info(f"Searching for pattern [{query}] in files matching [{include_pattern}]")
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


# Create the grep_search tool
grep_search_tool = Tool(
    name="filesys.grep_search",
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

# Register the tool
global_tool_registry.register_tool(grep_search_tool)