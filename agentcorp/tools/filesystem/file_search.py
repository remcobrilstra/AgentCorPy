"""
File search tool for the AgentCorp framework
"""

import glob
from pathlib import Path

from ...tool_registry import Tool, global_tool_registry, ToolExecutionContext
from ...logging import logger

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
        logger.info(f"Searching for files [{query}]")
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


# Create the file_search tool
file_search_tool = Tool(
    name="filesys.file_search",
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

# Register the tool
global_tool_registry.register_tool(file_search_tool)