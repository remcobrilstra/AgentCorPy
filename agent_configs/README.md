# Agent Configurations

This directory contains example agent configuration files in JSON format. These configurations can be loaded using the AgentCorp framework to create pre-configured agents.

## Configuration Format

Each agent configuration is a JSON file with the following structure:

```json
{
  "name": "AgentName",           // Optional: Human-readable name
  "description": "Description",  // Optional: Agent description
  "model": "model-name",         // Required: Model identifier
  "provider": "provider-name",   // Required: "openai" or "anthropic"
  "system_prompt": "Prompt",     // Required: System prompt
  "tools": ["tool1", "tool2"],   // Optional: List of tool names
  "context_settings": {          // Optional: Tool execution settings
    "setting1": "value1"
  }
}
```

## Example Configurations

### `code_assistant.json`
A coding assistant with file reading capabilities:
- Uses GPT-4 via OpenAI
- Has access to file reading tools
- Restricted to current directory for security

### `data_analyzer.json`
A data analysis agent with calculation tools:
- Uses Claude 3 Sonnet via Anthropic
- Has access to calculation and file reading tools
- Restricted to `./data` directory

### `minimal_assistant.json`
A basic assistant with no tools:
- Uses GPT-3.5-turbo via OpenAI
- No special tools or restrictions
- Good starting point for simple agents

## Usage

Load an agent from a configuration file:

```python
from agentcorp import load_agent_from_file

agent = load_agent_from_file("agent_configs/code_assistant.json")
```

Or create programmatically and save:

```python
from agentcorp import AgentConfig, create_agent_from_config, save_agent_config

config = AgentConfig(
    name="MyAgent",
    model="gpt-4",
    provider="openai",
    system_prompt="You are helpful.",
    tools=["read_file"]
)

agent = create_agent_from_config(config)
save_agent_config(agent, "my_agent.json")
```

## Security Considerations

- **Tool Access**: Only grant tools that agents actually need
- **Path Restrictions**: Use `context_settings.allowed_base_path` to limit file access
- **API Keys**: Never store API keys in configuration files
- **Context Settings**: Use settings to enforce security policies in tool implementations

## Creating Custom Configurations

1. Copy an existing configuration as a template
2. Modify the required fields (model, provider, system_prompt)
3. Add optional fields as needed (name, description, tools, context_settings)
4. Test with your specific use case
5. Save and version control your configurations