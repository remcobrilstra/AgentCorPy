# AgentCorp - Simple Agent Framework

from .agent import Agent
from .providers import Provider, Message, OpenAIProvider, AnthropicProvider
from .memory import Memory
from .tasks import TaskManager, Task, TaskStatus
from .tool_registry import Tool, ToolRegistry, ToolExecutionContext, global_tool_registry

# Import tool modules to register tools
from . import tools
from .config import AgentConfig, create_agent_from_config, load_agent_from_file, save_agent_config

try:
    from .providers import XAIProvider
    _xai_available = True
except ImportError:
    _xai_available = False
    XAIProvider = None

__all__ = [
    "Agent",
    "Provider", "Message", "OpenAIProvider", "AnthropicProvider",
    "Memory",
    "TaskManager", "Task", "TaskStatus",
    "Tool", "ToolRegistry", "ToolExecutionContext", "global_tool_registry",
    "AgentConfig", "create_agent_from_config", "load_agent_from_file", "save_agent_config"
]

if _xai_available:
    __all__.append("XAIProvider")