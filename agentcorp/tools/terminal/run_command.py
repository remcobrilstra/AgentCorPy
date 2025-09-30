"""
Run command tool for the AgentCorp framework
"""

import subprocess
import os
from pathlib import Path
from ...tool_registry import Tool, global_tool_registry, ToolExecutionContext
from ...logging import logger

def run_command(context: ToolExecutionContext, command: str, shell: str = "pwsh.exe") -> str:
    """
    Run a command in the terminal with the working directory set to the context's workingdir.

    Args:
        context: Tool execution context
        command: The command to run
        shell: The shell to use (default: pwsh.exe for Windows)

    Returns:
        str: Command output or error message
    """
    workingdir = context.get_setting("workingdir", "")

    if not workingdir:
        return "Error: No working directory set in context. Cannot run terminal commands without a working directory restriction."

    try:
        working_dir_path = Path(workingdir).resolve()
        if not working_dir_path.exists() or not working_dir_path.is_dir():
            return f"Error: Working directory {workingdir} does not exist or is not a directory"

        logger.info(f"Running command in working directory [{workingdir}]: {command}")

        # Run the command in a subprocess with the specified working directory
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(working_dir_path),
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )

        output = result.stdout
        if result.stderr:
            output += "\nSTDERR:\n" + result.stderr

        if result.returncode != 0:
            output = f"Command failed with return code {result.returncode}\n{output}"

        return output

    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds"
    except FileNotFoundError:
        return f"Error: Shell '{shell}' not found"
    except Exception as e:
        return f"Error running command: {e}"


# Create the run_command tool
run_command_tool = Tool(
    name="terminal.run_command",
    description="Run a command in the terminal. The working directory is set to the context's workingdir, and all operations are restricted to stay within that directory.",
    function=run_command,
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The command to execute in the terminal"
            },
            "shell": {
                "type": "string",
                "description": "The shell to use for executing the command (default: pwsh.exe)",
                "default": "pwsh.exe"
            }
        },
        "required": ["command"]
    }
)

# Register the tool
global_tool_registry.register_tool(run_command_tool)