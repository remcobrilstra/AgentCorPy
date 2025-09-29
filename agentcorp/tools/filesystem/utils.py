"""
Filesystem tools utilities for the AgentCorp framework
"""

import os
from pathlib import Path
from typing import Optional

from ...tool_registry import ToolExecutionContext


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