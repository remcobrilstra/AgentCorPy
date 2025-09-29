#!/usr/bin/env python3
"""
Integration tests for filesystem tools

This module tests the filesystem tools integration with the AgentCorp framework,
including working directory restrictions and tool execution contexts.
"""

import os
import sys
import tempfile
import shutil
import unittest
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentcorp import ToolExecutionContext, global_tool_registry


class TestFilesystemToolsIntegration(unittest.TestCase):
    """Integration tests for filesystem tools"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="agentcorp_test_"))
        self.restricted_context = ToolExecutionContext(
            settings={"workingdir": str(self.test_dir)},
            agent_id="test-agent"
        )
        self.unrestricted_context = ToolExecutionContext(
            settings={},
            agent_id="test-agent"
        )

        # Get tools from registry
        self.read_tool = global_tool_registry.get_tool("read_file")
        self.write_tool = global_tool_registry.get_tool("write_file")
        self.replace_tool = global_tool_registry.get_tool("replace_in_file")
        self.delete_tool = global_tool_registry.get_tool("delete_file")
        self.search_tool = global_tool_registry.get_tool("file_search")
        self.grep_tool = global_tool_registry.get_tool("grep_search")

    def tearDown(self):
        """Clean up test fixtures"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_tools_are_registered(self):
        """Test that all filesystem tools are properly registered"""
        expected_tools = ["read_file", "write_file", "replace_in_file", "delete_file", "file_search", "grep_search"]

        for tool_name in expected_tools:
            with self.subTest(tool=tool_name):
                tool = global_tool_registry.get_tool(tool_name)
                self.assertIsNotNone(tool, f"Tool {tool_name} is not registered")

    def test_write_and_read_file(self):
        """Test writing to and reading from a file"""
        test_file = self.test_dir / "test.txt"
        test_content = "Hello, AgentCorp!\nThis is a test file.\nLine 3 for testing."

        # Write file
        result = self.write_tool.execute(self.restricted_context,
                                       file_path=str(test_file),
                                       content=test_content)
        self.assertIn("Successfully wrote", result)
        self.assertTrue(test_file.exists())

        # Read file
        result = self.read_tool.execute(self.restricted_context, file_path=str(test_file))
        self.assertEqual(result, test_content)

    def test_replace_in_file(self):
        """Test replacing text in a file"""
        test_file = self.test_dir / "test.txt"
        original_content = "Hello, AgentCorp!\nThis is a test file."
        new_content = "Hello, AgentCorp Framework!\nThis is a test file."

        # Create file
        self.write_tool.execute(self.restricted_context,
                              file_path=str(test_file),
                              content=original_content)

        # Replace text
        result = self.replace_tool.execute(self.restricted_context,
                                         file_path=str(test_file),
                                         old_text="AgentCorp",
                                         new_text="AgentCorp Framework")
        self.assertIn("Successfully replaced 1 occurrence", result)

        # Verify replacement
        result = self.read_tool.execute(self.restricted_context, file_path=str(test_file))
        self.assertEqual(result, new_content)

    def test_delete_file(self):
        """Test deleting a file"""
        test_file = self.test_dir / "test.txt"

        # Create file
        self.write_tool.execute(self.restricted_context,
                              file_path=str(test_file),
                              content="Test content")

        # Delete file
        result = self.delete_tool.execute(self.restricted_context, file_path=str(test_file))
        self.assertIn("Successfully deleted", result)
        self.assertFalse(test_file.exists())

    def test_file_search_python_files(self):
        """Test searching for Python files"""
        # Create test files
        test_files = [
            (self.test_dir / "config.py", "# Configuration file"),
            (self.test_dir / "main.py", "# Main application"),
            (self.test_dir / "data.txt", "Some data"),
        ]

        for file_path, content in test_files:
            self.write_tool.execute(self.restricted_context,
                                  file_path=str(file_path),
                                  content=content)

        # Search for Python files
        result = self.search_tool.execute(self.restricted_context, query="**/*.py")
        self.assertIn("config.py", result)
        self.assertIn("main.py", result)
        self.assertNotIn("data.txt", result)

    def test_file_search_specific_directory(self):
        """Test searching in a specific directory"""
        # Create directory structure
        (self.test_dir / "src").mkdir(exist_ok=True)
        (self.test_dir / "src" / "main.py").write_text("# Main file")

        result = self.search_tool.execute(self.restricted_context, query="src/**/*")
        self.assertIn("main.py", result)

    def test_file_search_no_matches(self):
        """Test searching with no matches"""
        result = self.search_tool.execute(self.restricted_context, query="**/*.nonexistent")
        self.assertIn("No files found", result)

    def test_grep_search_plain_text(self):
        """Test grep search with plain text"""
        # Create test files
        test_files = [
            (self.test_dir / "config.py", "# Configuration file\n# Another comment"),
            (self.test_dir / "main.py", "# Main application\nprint('hello')"),
        ]

        for file_path, content in test_files:
            self.write_tool.execute(self.restricted_context,
                                  file_path=str(file_path),
                                  content=content)

        result = self.grep_tool.execute(self.restricted_context, query="#", include_pattern="**/*.py")
        self.assertIn("Configuration file", result)
        self.assertIn("Main application", result)

    def test_grep_search_regex(self):
        """Test grep search with regex"""
        # Create test file
        test_file = self.test_dir / "config.py"
        self.write_tool.execute(self.restricted_context,
                              file_path=str(test_file),
                              content="# Configuration file\ndef test():\n    pass")

        result = self.grep_tool.execute(self.restricted_context,
                                      query="def.*test",
                                      include_pattern="**/*.py",
                                      is_regexp=True)
        self.assertIn("def test():", result)

    def test_grep_search_no_matches(self):
        """Test grep search with no matches"""
        # Create a Python file first
        test_file = self.test_dir / "test.py"
        self.write_tool.execute(self.restricted_context,
                              file_path=str(test_file),
                              content="print('hello')")

        result = self.grep_tool.execute(self.restricted_context,
                                      query="nonexistent_pattern",
                                      include_pattern="**/*.py")
        self.assertIn("No matches found", result)

    def test_working_directory_restriction(self):
        """Test that working directory restrictions are enforced"""
        outside_file = Path.home() / "test_outside.txt"

        result = self.write_tool.execute(self.restricted_context,
                                       file_path=str(outside_file),
                                       content="This should fail")
        self.assertIn("Access denied", result)

    def test_unrestricted_access(self):
        """Test that unrestricted context allows access outside working directory"""
        temp_outside = Path(tempfile.mkdtemp()) / "unrestricted_test.txt"

        try:
            result = self.write_tool.execute(self.unrestricted_context,
                                           file_path=str(temp_outside),
                                           content="This should work")
            self.assertIn("Successfully wrote", result)
            self.assertTrue(temp_outside.exists())
        finally:
            # Clean up
            if temp_outside.exists():
                temp_outside.unlink()
            temp_outside.parent.rmdir()

    def test_error_handling_missing_file(self):
        """Test error handling when trying to read a non-existent file"""
        nonexistent_file = self.test_dir / "nonexistent.txt"

        result = self.read_tool.execute(self.restricted_context, file_path=str(nonexistent_file))
        self.assertIn("does not exist", result)

    def test_tool_schema_formats(self):
        """Test that tools can be converted to different provider formats"""
        tools_to_test = ["read_file", "write_file", "replace_in_file", "delete_file", "file_search", "grep_search"]

        for tool_name in tools_to_test:
            with self.subTest(tool=tool_name):
                tool = global_tool_registry.get_tool(tool_name)

                # Test OpenAI format
                openai_format = tool.to_openai_format()
                self.assertEqual(openai_format['function']['name'], tool_name)
                self.assertIn('parameters', openai_format['function'])

                # Test Anthropic format
                anthropic_format = tool.to_anthropic_format()
                self.assertEqual(anthropic_format['name'], tool_name)
                self.assertIn('input_schema', anthropic_format)

    def test_write_file_with_directory_creation(self):
        """Test that write_file creates parent directories when requested"""
        nested_file = self.test_dir / "subdir" / "nested" / "file.txt"

        result = self.write_tool.execute(self.restricted_context,
                                       file_path=str(nested_file),
                                       content="Test content",
                                       create_dirs=True)
        self.assertIn("Successfully wrote", result)
        self.assertTrue(nested_file.exists())
        self.assertTrue(nested_file.parent.exists())


if __name__ == "__main__":
    # Import tools to ensure registration
    import agentcorp.tools

    unittest.main()