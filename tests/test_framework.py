#!/usr/bin/env python3
"""
Simple test for the complex task functionality
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from agentcorp import Agent, Task, TaskManager, TaskStatus, Tool, global_tool_registry, ToolExecutionContext


def test_task_hierarchy():
    """Test basic task hierarchy functionality"""
    print("Testing task hierarchy...")

    # Create a complex task
    task_manager = TaskManager()
    task_id = task_manager.add_complex_task(
        "Build a website",
        ["Design the layout", "Write HTML code", "Add CSS styling", "Test functionality"]
    )

    task = task_manager.get_task(task_id)
    assert task.description == "Build a website"
    assert len(task.subtasks) == 4
    assert task.is_complex()

    # Test subtask relationships
    for subtask in task.subtasks:
        assert subtask.parent_task == task
        assert not subtask.is_complex()

    print("[PASS] Task hierarchy test passed")


def test_task_execution():
    """Test task execution functionality"""
    print("Testing task execution...")

    task_manager = TaskManager()

    # Create a simple task
    task_id = task_manager.add_task("Simple task")
    task = task_manager.get_task(task_id)

    # Mock agent with chat method
    class MockAgent:
        def chat(self, prompt, add_to_memory=True):
            return f"Executed via LLM: {prompt.split('Current task to complete:')[-1].strip()}"

    agent = MockAgent()
    result = task.execute(agent)
    assert "Executed via LLM: Simple task" in result

    print("[PASS] Task execution test passed")


def test_sequential_execution():
    """Test sequential task execution"""
    print("Testing sequential execution...")

    task_manager = TaskManager()

    # Create complex task
    task_id = task_manager.add_complex_task(
        "Process data",
        ["Load data", "Clean data", "Analyze data"]
    )

    task = task_manager.get_task(task_id)

    # Mock agent with chat method
    execution_count = 0
    class MockAgent:
        def chat(self, prompt, add_to_memory=True):
            nonlocal execution_count
            execution_count += 1
            task_desc = prompt.split('Current task to complete:')[-1].strip()
            return f"Step {execution_count}: {task_desc}"

    agent = MockAgent()
    result = task_manager.execute_task_sequentially(agent, task_id)

    # Check that all subtasks were executed
    assert execution_count == 4  # 3 subtasks + 1 main task
    assert task.status == TaskStatus.COMPLETED

    print("[PASS] Sequential execution test passed")


def test_tool_context():
    """Test tool context functionality"""
    print("Testing tool context...")

    # Create a test tool (don't clear the global registry)
    def test_func(context, value):
        return f"Processed {value} with setting: {context.get_setting('test_setting', 'default')}"

    tool = Tool(
        name="test_tool",
        description="Test tool",
        function=test_func,
        parameters={"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"]}
    )

    global_tool_registry.register_tool(tool)

    # Create context
    context = ToolExecutionContext(settings={"test_setting": "test_value"}, agent_id="test-agent")

    # Test tool execution with context
    result = global_tool_registry.execute_tool({
        "function": {"name": "test_tool", "arguments": '{"value": "hello"}'}
    }, context)

    assert "Processed hello with setting: test_value" in result
    print("[PASS] Tool context test passed")


def test_web_fetch():
    """Test web_fetch tool functionality"""
    print("Testing web_fetch tool...")
    print(f"Available tools: {list(global_tool_registry.tools.keys())}")

    try:
        # Test with a simple static page
        context = ToolExecutionContext(settings={}, agent_id="test-agent")

        # Test with a simple static HTML page
        result = global_tool_registry.execute_tool({
            "function": {"name": "web_fetch", "arguments": '{"url": "https://httpbin.org/html"}'}
        }, context)

        print(f"Result type: {type(result)}")
        print(f"Result length: {len(result) if isinstance(result, str) else 'N/A'}")

        # Check that we got markdown content back
        assert isinstance(result, str), f"Expected str, got {type(result)}"
        assert len(result) > 0, "Result is empty"
        assert "# Herman Melville" in result, f"'# Herman Melville' not found in result: {result[:200]}"

        print("[PASS] Web fetch test passed")
    except Exception as e:
        print(f"[FAIL] Web fetch test failed: {e}")
        raise


if __name__ == "__main__":
    print("Running framework tests...\n")

    try:
        test_task_hierarchy()
        test_task_execution()
        test_sequential_execution()
        test_tool_context()
        test_web_fetch()

        print("\n[OK] All tests passed! Framework is ready for complex task and tool context handling.")

    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        sys.exit(1)