# AgentCorp - Simple Agent Fra# Register tools in global registry
from agentcorp import global_tool_registry

tool = Tool(name="my_tool", description="...", function=my_func, parameters={...})
global_tool_registry.register_tool(tool)

# Create agent with specific tools and context
agent = Agent(
    provider=provider,
    system_prompt="You are a helpful assistant.",
    tool_names=["my_tool"],  # Specify which tools this agent can use
    context_settings={
        "allowed_paths": "/safe/path",
        "max_operations": "10"
    }
)

# Load agent from configuration file
agent = load_agent_from_file("path/to/agent_config.json")

# Save agent configuration
save_agent_config(agent, "path/to/agent_config.json")le Python framework for building AI agents that abstracts away different LLM provider SDKs.

## Features

- **Provider Abstraction**: Unified interface for OpenAI, Anthropic, and xAI
- **Agent Concept**: Agents with model/provider, tools, system prompts, memory, and task tracking
- **Memory Management**: Conversation history with configurable limits
- **Task Tracking**: Keep track of current tasks for longer running operations
- **Tool Integration**: Support for function calling/tools with compatible providers
- **Complex Task Handling**: Automatic decomposition of complex tasks into subtasks with sequential execution
- **Tool Context System**: Context-aware tool execution with security settings and restrictions
- **Built-in Tools**: Framework includes web scraping tools for content retrieval
- **Agent Configuration**: Load and save agent configurations from/to JSON files

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the environment: `.venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install openai anthropic xai`

## Usage

```python
from agentcorp import Agent, OpenAIProvider, Tool, ToolRegistry

# Create provider
provider = OpenAIProvider(api_key="your-openai-key")

# Register tools in global registry
from agentcorp import global_tool_registry

tool = Tool(name="my_tool", description="...", function=my_function, parameters={...})
global_tool_registry.register_tool(tool)

# Create agent with specific tools and context
agent = Agent(
    provider=provider,
    system_prompt="You are a helpful assistant.",
    tool_names=["my_tool"],  # Specify which tools this agent can use
    context_settings={
        "allowed_paths": "/safe/path",
        "max_operations": "10"
    }
)

# Chat
response = agent.chat("Hello!")
print(response)

# Manage tasks
task_id = agent.add_task("Analyze data")
tasks = agent.get_tasks()
agent.update_task(task_id, "completed")

# Handle complex tasks automatically
response = agent.handle_complex_query("Plan a complete software development project")
print(response)

# Manual task decomposition and execution
task_id = agent.decompose_task("Write a research paper on AI ethics")
result = agent.execute_task_sequentially(task_id)
print(result)
```

## Development Guidelines

This project uses GitHub Copilot with specific instructions defined in `.github/copilot-instructions.md`. Key guidelines for contributors:

- **Dependencies**: Always prefer existing dependencies over adding new ones
- **Environment**: Always use the virtual environment (`.venv/`) for all Python operations
- **Documentation**: Update this README.md for any changes affecting framework usage

## Agent Configuration Files

Agents can be defined using JSON configuration files. Example structure:

```json
{
  "name": "MyAgent",
  "description": "A helpful assistant",
  "model": "gpt-4",
  "provider": "openai",
  "system_prompt": "You are a helpful assistant.",
  "tools": ["tool1", "tool2"],
  "context_settings": {
    "setting1": "value1"
  }
}
```

See `agent_configs/` directory for example configurations and `examples/agent_config_example.py` for usage.

## Supported Providers

- **OpenAI**: GPT models with tool calling
- **Anthropic**: Claude models with tool calling
- **xAI**: Grok models (tool calling not yet supported)

## Running the Example

Set your API key as an environment variable:

```bash
export OPENAI_API_KEY="your-key-here"
python example.py
```

Or for Anthropic:

```bash
export ANTHROPIC_API_KEY="your-key-here"
export PROVIDER=anthropic
python example.py
```

## Built-in Tools

The framework includes several built-in tools that are automatically available:

### Web Fetch Tool

Fetch content from URLs and convert it to markdown format.

```python
# The web_fetch tool is automatically registered
result = agent.chat("Fetch the content from https://example.com")
```

Parameters:
- `url` (string, required): The URL to fetch content from
- `render_js` (boolean, optional): Whether to render JavaScript for client-side content (default: false)

Example usage with JavaScript rendering:
```python
# For sites that require JavaScript execution
result = global_tool_registry.execute_tool({
    "function": {"name": "web_fetch", "arguments": '{"url": "https://example.com", "render_js": true}'}
}, context)
```