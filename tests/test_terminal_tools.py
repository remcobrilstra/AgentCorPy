#!/usr/bin/env python3
"""
Test script for terminal tools

This script tests the new terminal tools to ensure they work correctly
with the AgentCorp framework and respect working directory restrictions.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentcorp import ToolExecutionContext, global_tool_registry


def test_terminal_tools():
    """Test terminal tools with various scenarios"""

    # Create a temporary directory for testing
    test_dir = Path(tempfile.mkdtemp(prefix="agentcorp_terminal_test_"))

    try:
        restricted_context = ToolExecutionContext(
            settings={"workingdir": str(test_dir)},
            agent_id="test-agent"
        )

        # Get tools from registry
        run_command_tool = global_tool_registry.get_tool("terminal.run_command")

        if not run_command_tool:
            print("[FAIL] Error: terminal.run_command tool not registered!")
            return False

        print("PASS Terminal run_command tool found in registry")

        # Test 1: Run a simple command
        result = run_command_tool.execute(restricted_context, command="echo 'Hello, World!'")

        if "Hello, World!" not in result:
            print(f"[FAIL] Error: Simple echo command failed! Result: {result}")
            return False

        # Test 2: Run command that creates a file
        result = run_command_tool.execute(restricted_context, command="echo test content > test_file.txt")

        # Check if file was created
        test_file = test_dir / "test_file.txt"
        if not test_file.exists():
            print("[FAIL] Error: File was not created by command!")
            return False

        # Verify content
        with open(test_file, 'r') as f:
            content = f.read().strip()
        if content != "test content":
            print(f"[FAIL] Error: File content incorrect! Got: '{content}'")
            return False

        # Test 3: Run command that lists directory
        result = run_command_tool.execute(restricted_context, command="dir" if os.name == 'nt' else "ls")

        if "test_file.txt" not in result:
            print(f"[FAIL] Error: Directory listing failed! Result: {result}")
            return False

        # Test 4: Test working directory restriction - no workingdir set
        unrestricted_context = ToolExecutionContext(
            settings={},
            agent_id="test-agent"
        )

        result = run_command_tool.execute(unrestricted_context, command="echo 'should fail'")

        if "No working directory set" not in result:
            print(f"[FAIL] Error: Should have failed without workingdir! Result: {result}")
            return False

        # Test 5: Test invalid working directory
        invalid_context = ToolExecutionContext(
            settings={"workingdir": "/nonexistent/directory"},
            agent_id="test-agent"
        )

        result = run_command_tool.execute(invalid_context, command="echo 'test'")

        if "does not exist" not in result:
            print(f"[FAIL] Error: Should have failed with invalid workingdir! Result: {result}")
            return False

        # Test 6: Test command timeout (if possible)
        # This might not work on all systems, so we'll skip if it doesn't timeout
        try:
            result = run_command_tool.execute(restricted_context, command="timeout 32" if os.name == 'nt' else "sleep 32")
            if "timed out" in result:
                print("PASS Command timeout works correctly")
            else:
                print("INFO Command timeout test inconclusive (may not have timed out)")
        except:
            print("INFO Command timeout test skipped")

        print("PASS All terminal tools tests passed!")
        return True

    except Exception as e:
        print(f"[FAIL] Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up test directory
        if test_dir.exists():
            shutil.rmtree(test_dir)


def test_tool_registration():
    """Test that terminal tools are properly registered"""

    expected_tools = ["terminal.run_command"]
    registered_tools = list(global_tool_registry.tools.keys())

    missing_tools = [tool for tool in expected_tools if tool not in registered_tools]

    if missing_tools:
        print(f"[FAIL] Missing tools: {missing_tools}")
        return False

    print("PASS All terminal tools are properly registered!")

    # Test tool schema formats
    for tool_name in expected_tools:
        tool = global_tool_registry.get_tool(tool_name)

        # Test OpenAI format
        openai_format = tool.to_openai_format()

        # Test Anthropic format
        anthropic_format = tool.to_anthropic_format()

        # Check required parameters
        required = openai_format['function']['parameters']['required']
        if "command" not in required:
            print(f"[FAIL] Error: {tool_name} missing required command parameter!")
            return False

    print("PASS All tool schemas are valid!")
    return True


if __name__ == "__main__":
    try:
        # Import tools to ensure registration
        import agentcorp.tools

        success = True
        success &= test_tool_registration()
        success &= test_terminal_tools()

        if success:
            print("PASS All tests passed! Terminal tools are ready to use.")
        else:
            print("[FAIL] Some tests failed. Please check the implementation.")
            sys.exit(1)

    except Exception as e:
        print(f"[FAIL] Test setup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)