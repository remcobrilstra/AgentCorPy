#!/usr/bin/env python3
"""
Programmer Agent Example

This example demonstrates a programmer agent that:
1. Loads agent configuration from programmer_agent_config.json
2. Sets up a workspace from a simulated git repository
3. Receives a programming task
4. Iteratively works on the task until completion
5. Uses filesystem tools for code manipulation

The agent configuration is stored in programmer_agent_config.json alongside this file.

Supported providers: OpenAI, Anthropic, xAI (set PROVIDER environment variable)

To see detailed logging of tool calls and task actions, set AGENTCORP_VERBOSE=true

This showcases the AgentCorp framework's capabilities for complex,
multi-step software development tasks.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentcorp import Agent, OpenAIProvider, AnthropicProvider, XAIProvider, ToolExecutionContext, global_tool_registry, load_agent_from_file, AgentConfig

def create_simulated_git_repo(work_dir: Path) -> None:
    """Create a simulated git repository with sample code files."""
    print("🔧 Setting up simulated git repository...")

    # Create project structure
    (work_dir / "src").mkdir(exist_ok=True)
    (work_dir / "tests").mkdir(exist_ok=True)
    (work_dir / "docs").mkdir(exist_ok=True)

    # Create main.py
    main_py = '''#!/usr/bin/env python3
"""
Simple Calculator Application

A basic calculator that performs arithmetic operations.
"""

class Calculator:
    """A simple calculator class."""

    def __init__(self):
        """Initialize the calculator."""
        self.result = 0

    def add(self, a, b):
        """Add two numbers."""
        return a + b

    def subtract(self, a, b):
        """Subtract two numbers."""
        return a - b

    def multiply(self, a, b):
        """Multiply two numbers."""
        return a + b  # BUG: Should be a * b

    def divide(self, a, b):
        """Divide two numbers."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b


def main():
    """Main function."""
    calc = Calculator()

    # Simple demonstration
    print("Calculator Demo:")
    print(f"2 + 3 = {calc.add(2, 3)}")
    print(f"5 - 2 = {calc.subtract(5, 2)}")
    print(f"4 * 3 = {calc.multiply(4, 3)}")  # This will show the bug
    print(f"8 / 2 = {calc.divide(8, 2)}")


if __name__ == "__main__":
    main()
'''

    # Create test file
    test_py = '''#!/usr/bin/env python3
"""
Tests for the Calculator class.
"""

import unittest
from src.calculator import Calculator


class TestCalculator(unittest.TestCase):
    """Test cases for Calculator."""

    def setUp(self):
        """Set up test fixtures."""
        self.calc = Calculator()

    def test_add(self):
        """Test addition."""
        self.assertEqual(self.calc.add(2, 3), 5)
        self.assertEqual(self.calc.add(-1, 1), 0)

    def test_subtract(self):
        """Test subtraction."""
        self.assertEqual(self.calc.subtract(5, 2), 3)
        self.assertEqual(self.calc.subtract(1, 1), 0)

    def test_multiply(self):
        """Test multiplication."""
        self.assertEqual(self.calc.multiply(4, 3), 12)
        self.assertEqual(self.calc.multiply(0, 5), 0)

    def test_divide(self):
        """Test division."""
        self.assertEqual(self.calc.divide(8, 2), 4)
        self.assertEqual(self.calc.divide(5, 2), 2.5)

    def test_divide_by_zero(self):
        """Test division by zero raises error."""
        with self.assertRaises(ValueError):
            self.calc.divide(5, 0)


if __name__ == "__main__":
    unittest.main()
'''

    # Create README
    readme_md = '''# Calculator Project

A simple calculator application with basic arithmetic operations.

## Features

- Addition
- Subtraction
- Multiplication
- Division

## Usage

```bash
python src/calculator.py
```

## Testing

```bash
python -m pytest tests/
```
'''

    # Write files
    write_tool = global_tool_registry.get_tool("write_file")
    context = ToolExecutionContext(settings={}, agent_id="setup", session_id="setup")

    write_tool.execute(context, file_path=str(work_dir / "src" / "calculator.py"), content=main_py)
    write_tool.execute(context, file_path=str(work_dir / "tests" / "test_calculator.py"), content=test_py)
    write_tool.execute(context, file_path=str(work_dir / "README.md"), content=readme_md)

    print("✅ Simulated git repository created with sample calculator project")

def create_programmer_agent(work_dir: Path):
    """Create a programmer agent by loading configuration from file."""
    # Load agent configuration from file
    config_path = Path(__file__).parent / "programmer_agent_config.json"

    agent = load_agent_from_file(config_path)
    
    # Update context settings with working directory
    agent.execution_context.settings["workingdir"] = str(work_dir)

    print(f"✅ Loaded programmer agent from {config_path}")
    return agent

def demonstrate_programmer_agent_workflow():
    """Demonstrate the complete programmer agent workflow."""

    print("🚀 Programmer Agent Workflow Demonstration")
    print("=" * 50)

    # Create temporary workspace
    work_dir = Path(tempfile.mkdtemp(prefix="programmer_agent_demo_"))
    print(f"📁 Workspace created: {work_dir}")

    try:
        # Step 1: Set up simulated git repository
        create_simulated_git_repo(work_dir)

        # Step 2: Create programmer agent
        agent = create_programmer_agent(work_dir)

        # Step 3: Define programming task
        task = """
        Improve the calculator application by:
        1. Fixing the bug in the multiply method (currently uses + instead of *)
        2. Adding a power function (exponentiation) to the Calculator class
        3. Updating the tests to cover the new power function
        4. Updating the README to document the new feature
        """

        print(f"\n🎯 Task Assigned: {task.strip()}")

        # Step 4: Execute task iteratively
        print("\n⚡ Starting iterative task execution...")

        
        result = agent.handle_complex_query(task)
        print(f"Result: {result}")
    
        # Step 5: Verify results
        print("\n✅ Verifying results...")
        verify_changes(work_dir)

        print("\n🎉 Programmer agent workflow completed successfully!")

    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        if work_dir.exists():
            shutil.rmtree(work_dir)
            print(f"🧹 Cleaned up workspace: {work_dir}")

     
def verify_changes(work_dir: Path):
    """Verify that the agent's changes were applied correctly."""
    context = ToolExecutionContext(settings={"workingdir": str(work_dir)}, agent_id="verify", session_id="verify")
    read_tool = global_tool_registry.get_tool("read_file")
    grep_tool = global_tool_registry.get_tool("grep_search")

    print("🔍 Verification Results:")

    # Check multiply method fix
    if grep_tool:
        result = grep_tool.execute(context, query="return a \\* b", include_pattern="src/calculator.py")
        if "return a * b" in str(result) or "matches" in str(result):
            print("   ✅ Multiply method bug fixed")
        else:
            print("   ❌ Multiply method bug not fixed")
    else:
        # Fallback: manually check the file
        try:
            with open(work_dir / "src" / "calculator.py", 'r') as f:
                content = f.read()
            if "return a * b" in content:
                print("   ✅ Multiply method bug fixed")
            else:
                print("   ❌ Multiply method bug not fixed")
        except Exception as e:
            print(f"   ❌ Error checking multiply method: {e}")

    # Check power function added
    if grep_tool:
        result = grep_tool.execute(context, query="def power", include_pattern="src/calculator.py")
        if result and "matches" in str(result):
            print("   ✅ Power function added")
        else:
            print("   ❌ Power function not added")
    else:
        # Fallback: manually check the file
        try:
            with open(work_dir / "src" / "calculator.py", 'r') as f:
                content = f.read()
            if "def power" in content:
                print("   ✅ Power function added")
            else:
                print("   ❌ Power function not added")
        except Exception as e:
            print(f"   ❌ Error checking power function: {e}")

    # Check tests updated
    if grep_tool:
        result = grep_tool.execute(context, query="test_power", include_pattern="tests/test_calculator.py")
        if result and "matches" in str(result):
            print("   ✅ Power function tests added")
        else:
            print("   ❌ Power function tests not added")
    else:
        # Fallback: manually check the file
        try:
            with open(work_dir / "tests" / "test_calculator.py", 'r') as f:
                content = f.read()
            if "def test_power" in content:
                print("   ✅ Power function tests added")
            else:
                print("   ❌ Power function tests not added")
        except Exception as e:
            print(f"   ❌ Error checking tests: {e}")

    # Check README updated
    if read_tool:
        result = read_tool.execute(context, file_path=str(work_dir / "README.md"))
        if "Exponentiation" in str(result):
            print("   ✅ README updated")
        else:
            print("   ❌ README not updated")
    else:
        # Fallback: manually check the file
        try:
            with open(work_dir / "README.md", 'r') as f:
                content = f.read()
            if "Exponentiation" in content:
                print("   ✅ README updated")
            else:
                print("   ❌ README not updated")
        except Exception as e:
            print(f"   ❌ Error checking README: {e}")


if __name__ == "__main__":
    # Import tools to ensure they're registered
    import agentcorp.tools
    import agentcorp.tools.filesystem  # Import filesystem tools

    demonstrate_programmer_agent_workflow()