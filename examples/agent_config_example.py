#!/usr/bin/env python3
"""
Agent Configuration Example

This example demonstrates loading agents from JSON configuration files.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentcorp import (
    load_agent_from_file,
    AgentConfig,
    create_agent_from_config,
    save_agent_config,
    Tool,
    global_tool_registry
)


def setup_example_tools():
    """Set up some example tools for the demonstration"""

    def read_file_tool(context, file_path: str) -> str:
        """Read a file (simplified for demo)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"File content ({len(content)} chars): {content[:200]}{'...' if len(content) > 200 else ''}"
        except Exception as e:
            return f"Error reading file: {e}"

    def calculate_tool(context, expression: str) -> str:
        """Simple calculator"""
        try:
            # Very basic security - don't use eval in production!
            result = eval(expression, {"__builtins__": {}})
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {e}"

    # Register tools
    file_tool = Tool(
        name="read_file",
        description="Read the contents of a file",
        function=read_file_tool,
        parameters={
            "type": "object",
            "properties": {"file_path": {"type": "string", "description": "Path to file"}},
            "required": ["file_path"]
        }
    )

    calc_tool = Tool(
        name="calculate",
        description="Calculate mathematical expressions",
        function=calculate_tool,
        parameters={
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "Math expression"}},
            "required": ["expression"]
        }
    )

    global_tool_registry.register_tool(file_tool)
    global_tool_registry.register_tool(calc_tool)


def demonstrate_loading_from_file():
    """Demonstrate loading agents from configuration files"""

    print("=== Loading Agents from Configuration Files ===\n")

    config_dir = Path(__file__).parent.parent / "agent_configs"

    # Load Code Assistant
    print("1. Loading Code Assistant...")
    code_assistant = load_agent_from_file(str(config_dir / "code_assistant.json"))
    print(f"   Name: {code_assistant.name}")
    print(f"   Description: {code_assistant.description}")
    print(f"   Model: {code_assistant.provider.model}")
    print(f"   Tools: {list(code_assistant.tools.tools.keys())}")
    print(f"   Context settings: {code_assistant.execution_context.settings}")
    print()

    # Load Data Analyzer
    print("2. Loading Data Analyzer...")
    data_analyzer = load_agent_from_file(str(config_dir / "data_analyzer.json"))
    print(f"   Name: {data_analyzer.name}")
    print(f"   Description: {data_analyzer.description}")
    print(f"   Model: {data_analyzer.provider.model}")
    print(f"   Tools: {list(data_analyzer.tools.tools.keys())}")
    print(f"   Context settings: {data_analyzer.execution_context.settings}")
    print()

    # Load Minimal Assistant
    print("3. Loading Minimal Assistant...")
    minimal_assistant = load_agent_from_file(str(config_dir / "minimal_assistant.json"))
    print(f"   Name: {minimal_assistant.name}")
    print(f"   Description: {minimal_assistant.description}")
    print(f"   Model: {minimal_assistant.provider.model}")
    print(f"   Tools: {list(minimal_assistant.tools.tools.keys())}")
    print()


def demonstrate_programmatic_creation():
    """Demonstrate creating agents programmatically from config objects"""

    print("=== Programmatic Agent Creation ===\n")

    # Create config programmatically
    config = AgentConfig(
        name="CustomAgent",
        description="An agent created programmatically",
        model="gpt-4",
        provider="openai",
        system_prompt="You are a custom agent created from code.",
        tools=["read_file"],
        context_settings={"custom_setting": "custom_value"}
    )

    print("Created config:")
    print(f"  Name: {config.name}")
    print(f"  Description: {config.description}")
    print(f"  Model: {config.model}")
    print(f"  Tools: {config.tools}")
    print()

    # Create agent from config
    agent = create_agent_from_config(config)
    print("Created agent from config:")
    print(f"  Name: {agent.name}")
    print(f"  Description: {agent.description}")
    print(f"  Model: {agent.provider.model}")
    print()


def demonstrate_saving_configs():
    """Demonstrate saving agent configurations"""

    print("=== Saving Agent Configurations ===\n")

    # Create an agent programmatically
    from agentcorp import OpenAIProvider, Agent

    provider = OpenAIProvider("dummy-key", model="gpt-4")
    agent = Agent(
        provider=provider,
        system_prompt="You are a test agent.",
        tool_names=["calculate"],
        context_settings={"test": "value"}
    )
    agent.name = "TestAgent"
    agent.description = "An agent for testing save functionality"

    # Save to file
    save_path = Path(__file__).parent.parent / "agent_configs" / "saved_agent.json"
    save_agent_config(agent, str(save_path))

    print(f"Saved agent configuration to: {save_path}")

    # Load it back to verify
    loaded_agent = load_agent_from_file(str(save_path))
    print("Loaded saved configuration:")
    print(f"  Name: {loaded_agent.name}")
    print(f"  Description: {loaded_agent.description}")
    print()


def demonstrate_json_string_configs():
    """Demonstrate working with JSON string configurations"""

    print("=== JSON String Configurations ===\n")

    # JSON string configuration
    json_config = '''
    {
      "name": "StringAgent",
      "description": "An agent created from a JSON string",
      "model": "gpt-3.5-turbo",
      "provider": "openai",
      "system_prompt": "You are an agent created from a JSON string configuration.",
      "tools": ["read_file"],
      "context_settings": {
        "source": "json_string",
        "version": "1.0"
      }
    }
    '''

    # Load from JSON string
    config = AgentConfig.from_json_string(json_config)
    agent = create_agent_from_config(config)

    print("Created agent from JSON string:")
    print(f"  Name: {agent.name}")
    print(f"  Description: {agent.description}")
    print(f"  Context source: {agent.execution_context.get_setting('source')}")
    print()


if __name__ == "__main__":
    try:
        setup_example_tools()
        demonstrate_loading_from_file()
        demonstrate_programmatic_creation()
        demonstrate_saving_configs()
        demonstrate_json_string_configs()

        print("✅ All agent configuration examples completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have set the OPENAI_API_KEY environment variable for the examples that use OpenAI.")