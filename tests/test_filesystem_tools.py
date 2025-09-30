#!/usr/bin/env python3
"""
Test script for filesystem tools

This script tests the new filesystem tools to ensure they work correctly
with the AgentCorp framework and respect working directory restrictions.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from agentcorp import ToolExecutionContext, global_tool_registry


def test_filesystem_tools():
    """Test all filesystem tools with various scenarios"""
    
    
    # Create a temporary directory for testing
    test_dir = Path(tempfile.mkdtemp(prefix="agentcorp_test_"))
    
    try:

        restricted_context = ToolExecutionContext(
            settings={"workingdir": str(test_dir)},
            agent_id="test-agent"
        )
        
        # Test 2: Create context without restrictions
        unrestricted_context = ToolExecutionContext(
            settings={},
            agent_id="test-agent"
        )
        
    # Get tools from registry
        read_tool = global_tool_registry.get_tool("filesys.read_file")
        write_tool = global_tool_registry.get_tool("filesys.write_file")
        replace_tool = global_tool_registry.get_tool("filesys.replace_in_file")
        delete_tool = global_tool_registry.get_tool("filesys.delete_file")
        search_tool = global_tool_registry.get_tool("filesys.file_search")
        grep_tool = global_tool_registry.get_tool("filesys.grep_search")

        if not all([read_tool, write_tool, replace_tool, delete_tool, search_tool, grep_tool]):
            print("[FAIL] Error: Not all filesystem tools are registered!")
            return False
        
        print("PASS All filesystem tools found in registry")
        
        # Test 3: Write a test file
        test_file = test_dir / "test.txt"
        test_content = "Hello, AgentCorp!\nThis is a test file.\nLine 3 for testing."
        
        result = write_tool.execute(restricted_context, 
                                  file_path=str(test_file), 
                                  content=test_content)
        
        if not test_file.exists():
            print("[FAIL] Error: File was not created!")
            return False
        
        # Test 4: Read the test file
        result = read_tool.execute(restricted_context, file_path=str(test_file))
        
        if result != test_content:
            print("[FAIL] Error: Read content doesn't match written content!")
            return False
        
        # Test 5: Replace text in file
        result = replace_tool.execute(restricted_context,
                                    file_path=str(test_file),
                                    old_text="AgentCorp",
                                    new_text="AgentCorp Framework")

        
        # Verify replacement
        result = read_tool.execute(restricted_context, file_path=str(test_file))
        if "AgentCorp Framework" not in result:
            print("[FAIL] Error: Text replacement failed!")
            return False
        
        # Test 5.1: Create additional test files for file_search
        # Create a directory structure for testing
        (test_dir / "src").mkdir(exist_ok=True)
        (test_dir / "docs").mkdir(exist_ok=True)
        (test_dir / "src" / "utils").mkdir(exist_ok=True)
        
        test_files = [
            (test_dir / "config.py", "# Configuration file"),
            (test_dir / "src" / "main.py", "# Main application"),
            (test_dir / "src" / "utils" / "helper.py", "# Helper functions"),
            (test_dir / "src" / "utils" / "constants.js", "// JavaScript constants"),
            (test_dir / "docs" / "README.md", "# Documentation"),
            (test_dir / "package.json", '{"name": "test"}'),
        ]
        
        for file_path, content in test_files:
            write_tool.execute(restricted_context, file_path=str(file_path), content=content)
        
        
        # Test 5.2: Search for Python files
        result = search_tool.execute(restricted_context, query="**/*.py")
        
        if "main.py" not in result or "helper.py" not in result:
            print("[FAIL] Error: Python file search failed!")
            return False
        
        # Test 5.3: Search in specific directory
        result = search_tool.execute(restricted_context, query="src/**/*")
        
        if "main.py" not in result:
            print("[FAIL] Error: Directory-specific search failed!")
            return False
        
        # Test 5.4: Search for specific file type
        result = search_tool.execute(restricted_context, query="*.json")
        
        if "package.json" not in result:
            print("[FAIL] Error: JSON file search failed!")
            return False
        
        # Test 5.5: Search with no results
        result = search_tool.execute(restricted_context, query="**/*.nonexistent")
        
        if "No files found" not in result:
            print("[FAIL] Error: No matches handling failed!")
            return False
        
        # Test 5.6: Test grep_search - plain text search
        result = grep_tool.execute(restricted_context, query="#", include_pattern="**/*.py")

        
        if "#" not in result or "config.py" not in result:
            print("[FAIL] Error: Plain text grep search failed!")
            return False
        
        # Test 5.7: Test grep_search - regex search
        result = grep_tool.execute(restricted_context, query="#.*file", include_pattern="**/*.py", is_regexp=True)

        
        if "Configuration file" not in result:
            print("[FAIL] Error: Regex grep search failed!")
            return False
        
        # Test 5.8: Test grep_search - no matches
        result = grep_tool.execute(restricted_context, query="nonexistent_pattern", include_pattern="**/*.py")
        
        if "No matches found" not in result:
            print("[FAIL] Error: No matches grep handling failed!")
            return False
        
        # Test 6: Test working directory restrictions
        outside_file = Path.home() / "test_outside.txt"
        
        result = write_tool.execute(restricted_context,
                                  file_path=str(outside_file),
                                  content="This should fail")
        
        if "Access denied" not in result:
            print("[FAIL] Error: Working directory restriction not enforced!")
            return False
        
        # Test 7: Test without working directory restriction
        temp_outside = Path(tempfile.mkdtemp()) / "unrestricted_test.txt"
        
        result = write_tool.execute(unrestricted_context,
                                  file_path=str(temp_outside),
                                  content="This should work")

        
        if temp_outside.exists():
            temp_outside.unlink()  # Clean up
            temp_outside.parent.rmdir()
        
        # Test 8: Delete file
        result = delete_tool.execute(restricted_context, file_path=str(test_file))

        
        if test_file.exists():
            print("[FAIL] Error: File was not deleted!")
            return False
        
        # Test 9: Error handling - try to read deleted file
        result = read_tool.execute(restricted_context, file_path=str(test_file))

        
        if "does not exist" not in result:
            print("[FAIL] Error: Error handling for missing file failed!")
            return False

        print("PASS All filesystem tools tests passed!")
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
    """Test that all filesystem tools are properly registered"""
    

    expected_tools = ["filesys.read_file", "filesys.write_file", "filesys.replace_in_file", "filesys.delete_file", "filesys.file_search", "filesys.grep_search"]
    registered_tools = list(global_tool_registry.tools.keys())
    
    
    missing_tools = [tool for tool in expected_tools if tool not in registered_tools]
    
    if missing_tools:
        print(f"[FAIL] Missing tools: {missing_tools}")
        return False
    
    print("PASS All filesystem tools are properly registered!")
    
    # Test tool schema formats
    for tool_name in expected_tools:
        tool = global_tool_registry.get_tool(tool_name)
        
        
        # Test OpenAI format
        openai_format = tool.to_openai_format()
        
        # Test Anthropic format
        anthropic_format = tool.to_anthropic_format()
        
        # Check required parameters
        if tool_name == "read_file":
            required = openai_format['function']['parameters']['required']
            if "file_path" not in required:
                print(f"[FAIL] Error: {tool_name} missing required file_path parameter!")
                return False
        
        elif tool_name == "write_file":
            required = openai_format['function']['parameters']['required']
            if not all(param in required for param in ["file_path", "content"]):
                print(f"[FAIL] Error: {tool_name} missing required parameters!")
                return False
    
    print("PASS All tool schemas are valid!")
    return True


if __name__ == "__main__":
    try:
        # Import tools to ensure registration
        import agentcorp.tools
        
        success = True
        success &= test_tool_registration()
        success &= test_filesystem_tools()
        
        if success:
            print("PASS All tests passed! Filesystem tools are ready to use.")
        else:
            print("[FAIL] Some tests failed. Please check the implementation.")
            sys.exit(1)
            
    except Exception as e:
        print(f"[FAIL] Test setup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)