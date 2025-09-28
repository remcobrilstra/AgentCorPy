#!/usr/bin/env python3
"""
Tool Context Example

This example demonstrates the enhanced tool system with:
- Central tool registry
- Agent-specific tool subsets
- Tool execution context with settings and restrictions
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentcorp import Agent, OpenAIProvider, AnthropicProvider, Tool, global_tool_registry, ToolExecutionContext


def file_reader_tool(context: ToolExecutionContext, file_path: str) -> str:
    """Read a file with path restrictions based on context"""
    allowed_base_path = context.get_setting("allowed_base_path", "")

    if allowed_base_path:
        # Resolve paths to prevent directory traversal
        try:
            full_path = Path(file_path).resolve()
            allowed_path = Path(allowed_base_path).resolve()

            if not str(full_path).startswith(str(allowed_path)):
                return f"Access denied: {file_path} is outside the allowed path {allowed_base_path}"
        except Exception as e:
            return f"Error resolving path: {e}"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"File content ({len(content)} chars):\n{content[:500]}{'...' if len(content) > 500 else ''}"
    except Exception as e:
        return f"Error reading file: {e}"


def calculator_tool(context: ToolExecutionContext, expression: str) -> str:
    """Simple calculator with operation limits"""
    max_operations = int(context.get_setting("max_operations", "10"))

    # Simple security check - limit operations
    if expression.count('+') + expression.count('-') + expression.count('*') + expression.count('/') > max_operations:
        return f"Expression too complex. Max operations allowed: {max_operations}"

    try:
        # Use eval with restricted globals (very basic security)
        result = eval(expression, {"__builtins__": {}})
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating: {e}"


def web_search_tool(context: ToolExecutionContext, query: str) -> str:
    """Mock web search with rate limiting"""
    max_searches = int(context.get_setting("max_searches_per_hour", "5"))
    agent_id = context.agent_id

    # In a real implementation, you'd track searches per agent per hour
    # For demo, we'll just show the context info
    return f"Web search results for '{query}' (Agent: {agent_id}, Max searches: {max_searches})"


def setup_tools():
    """Register tools in the global registry"""

    # File reader tool
    file_tool = Tool(
        name="read_file",
        description="Read the contents of a file (with path restrictions)",
        function=file_reader_tool,
        parameters={
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file to read"}
            },
            "required": ["file_path"]
        }
    )

    # Calculator tool
    calc_tool = Tool(
        name="calculate",
        description="Calculate mathematical expressions",
        function=calculator_tool,
        parameters={
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Mathematical expression to evaluate"}
            },
            "required": ["expression"]
        }
    )

    # Web search tool
    search_tool = Tool(
        name="web_search",
        description="Search the web for information",
        function=web_search_tool,
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    )

    # Register all tools
    global_tool_registry.register_tool(file_tool)
    global_tool_registry.register_tool(calc_tool)
    global_tool_registry.register_tool(search_tool)


def create_restricted_agent():
    """Create an agent with restricted tool access and context settings"""
    provider_name = os.getenv("PROVIDER", "openai")

    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")
        provider = OpenAIProvider(api_key, model="gpt-3.5-turbo")
    elif provider_name == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable required")
        provider = AnthropicProvider(api_key)
    else:
        raise ValueError("Unsupported provider")

    # Create agent with limited tools and restrictive context
    agent = Agent(
        provider=provider,
        system_prompt="You are a restricted assistant with limited tool access for security.",
        tool_names=["read_file", "calculate"],  # Only these tools, not web_search
        context_settings={
            "allowed_base_path": str(Path(__file__).parent.parent),  # Only access project directory
            "max_operations": "3",  # Limit calculator complexity
            "security_level": "restricted"
        }
    )

    return agent


def create_power_user_agent():
    """Create an agent with broader tool access and permissive settings"""
    provider_name = os.getenv("PROVIDER", "openai")

    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")
        provider = OpenAIProvider(api_key, model="gpt-3.5-turbo")
    elif provider_name == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable required")
        provider = AnthropicProvider(api_key)
    else:
        raise ValueError("Unsupported provider")

    # Create agent with all tools and permissive context
    agent = Agent(
        provider=provider,
        system_prompt="You are a power user assistant with full tool access.",
        tool_names=["read_file", "calculate", "web_search"],  # All available tools
        context_settings={
            "allowed_base_path": "C:\\",  # Broad file access (be careful!)
            "max_operations": "20",  # Complex calculations allowed
            "max_searches_per_hour": "50",  # High search limit
            "security_level": "power_user"
        }
    )

    return agent


def demonstrate_tool_context():
    """Demonstrate how tool context affects behavior"""

    print("=== Tool Context Demonstration ===\n")

    # Setup tools
    setup_tools()

    # Create different agents with different contexts
    print("1. Creating restricted agent...")
    restricted_agent = create_restricted_agent()

    print("2. Creating power user agent...")
    power_agent = create_power_user_agent()

    print("\n3. Testing file access restrictions:")

    # Test file access with restricted agent
    test_file = str(Path(__file__).parent.parent / "README.md")
    response = restricted_agent.chat(f"Read the file at {test_file}")
    print(f"Restricted agent: {response}")

    # Test file access outside allowed path
    outside_file = "C:\\Windows\\System32\\drivers\\etc\\hosts"
    response = restricted_agent.chat(f"Read the file at {outside_file}")
    print(f"Restricted agent (outside path): {response}")

    print("\n4. Testing calculator complexity limits:")

    # Simple calculation (should work)
    response = restricted_agent.chat("Calculate 2 + 3 * 4")
    print(f"Restricted agent (simple): {response}")

    # Complex calculation (should be limited)
    response = restricted_agent.chat("Calculate 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 10")
    print(f"Restricted agent (complex): {response}")

    print("\n5. Testing tool availability:")

    # Restricted agent trying to use unavailable tool
    response = restricted_agent.chat("Search the web for Python tutorials")
    print(f"Restricted agent (unavailable tool): {response}")

    # Power user agent using all tools
    response = power_agent.chat("Search the web for Python tutorials")
    print(f"Power user agent: {response}")

    print("\n6. Context information:")
    print(f"Restricted agent context settings: {restricted_agent.execution_context.settings}")
    print(f"Power user agent context settings: {power_agent.execution_context.settings}")


def demonstrate_manual_context():
    """Show how to manually create and use tool execution context"""

    print("\n=== Manual Context Usage ===\n")

    # Create a custom context
    custom_context = ToolExecutionContext(
        settings={
            "allowed_base_path": str(Path.home()),
            "max_operations": "5",
            "user_role": "admin"
        },
        agent_id="custom-agent-123",
        session_id="session-456",
        custom_field="additional_info"
    )

    print("Custom context created:")
    print(f"  Agent ID: {custom_context.agent_id}")
    print(f"  Session ID: {custom_context.session_id}")
    print(f"  Settings: {custom_context.settings}")
    print(f"  Custom field: {custom_context.custom_field}")

    # Manually execute a tool with context
    file_tool = global_tool_registry.get_tool("read_file")
    if file_tool:
        result = file_tool.execute(custom_context, file_path=str(Path(__file__)))
        print(f"\nManual tool execution result: {result[:100]}...")


if __name__ == "__main__":
    try:
        demonstrate_tool_context()
        demonstrate_manual_context()
        print("\n✅ Tool context demonstration completed!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have set the appropriate API key environment variables:")
        print("- OPENAI_API_KEY for OpenAI")
        print("- ANTHROPIC_API_KEY for Anthropic")