from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
import os


@dataclass
class AgentConfig:
    """Configuration for creating an Agent instance"""
    model: str
    provider: str
    system_prompt: str
    tools: List[str]
    name: Optional[str] = None
    description: Optional[str] = None
    context_settings: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.context_settings is None:
            self.context_settings = {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentConfig':
        """Create AgentConfig from dictionary"""
        return cls(
            name=data.get('name'),
            description=data.get('description'),
            model=data['model'],
            provider=data['provider'],
            system_prompt=data['system_prompt'],
            tools=data.get('tools', []),
            context_settings=data.get('context_settings', {})
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_json_file(cls, file_path: str) -> 'AgentConfig':
        """Load configuration from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_json_file(self, file_path: str):
        """Save configuration to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def from_json_string(cls, json_str: str) -> 'AgentConfig':
        """Create AgentConfig from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_json_string(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


def create_agent_from_config(config: AgentConfig, api_keys: Optional[Dict[str, str]] = None) -> 'Agent':
    """Create an Agent instance from configuration

    Args:
        config: AgentConfig object
        api_keys: Dictionary of API keys, keyed by provider name
    """
    from .providers import OpenAIProvider, AnthropicProvider

    # Get API key
    if api_keys and config.provider in api_keys:
        api_key = api_keys[config.provider]
    else:
        # Try environment variables
        env_var = f"{config.provider.upper()}_API_KEY"
        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(f"API key not provided for provider {config.provider}. "
                           f"Set {env_var} environment variable or pass api_keys parameter.")

    # Create provider
    if config.provider.lower() == "openai":
        provider = OpenAIProvider(api_key, model=config.model)
    elif config.provider.lower() == "anthropic":
        provider = AnthropicProvider(api_key)
    else:
        raise ValueError(f"Unsupported provider: {config.provider}")

    # Import Agent here to avoid circular imports
    from .agent import Agent

    # Create agent
    agent = Agent(
        provider=provider,
        system_prompt=config.system_prompt,
        tool_names=config.tools,
        context_settings=config.context_settings
    )

    # Set optional attributes if provided
    if config.name:
        agent.name = config.name
    if config.description:
        agent.description = config.description

    return agent


def load_agent_from_file(file_path: str, api_keys: Optional[Dict[str, str]] = None) -> 'Agent':
    """Load an agent from a JSON configuration file"""
    config = AgentConfig.from_json_file(file_path)
    return create_agent_from_config(config, api_keys)


def save_agent_config(agent: 'Agent', file_path: str):
    """Save an agent's configuration to a JSON file"""
    config = AgentConfig(
        name=getattr(agent, 'name', None),
        description=getattr(agent, 'description', None),
        model=agent.provider.model,
        provider=agent.provider.__class__.__name__.replace('Provider', '').lower(),
        system_prompt=agent.memory.messages[0].content if agent.memory.messages and agent.memory.messages[0].role == 'system' else '',
        tools=list(agent.tools.tools.keys()),
        context_settings=agent.execution_context.settings
    )
    config.to_json_file(file_path)