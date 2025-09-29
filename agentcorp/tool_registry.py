from typing import List, Dict, Any, Callable, Optional


class ToolExecutionContext:
    """Context object passed to tools during execution"""
    def __init__(self, settings: Optional[Dict[str, str]] = None, agent_id: str = "", session_id: str = "", **kwargs):
        self.settings = settings or {}
        self.agent_id = agent_id
        self.session_id = session_id
        # Additional context can be added via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_setting(self, key: str, default: str = "") -> str:
        """Get a setting value"""
        return self.settings.get(key, default)

    def has_setting(self, key: str) -> bool:
        """Check if a setting exists"""
        return key in self.settings


class Tool:
    def __init__(self, name: str, description: str, function: Callable, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters

    def to_openai_format(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

    def to_anthropic_format(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters
        }

    def execute(self, context: ToolExecutionContext, **kwargs) -> Any:
        """Execute the tool with context"""
        return self.function(context, **kwargs)


class ToolRegistry:
    """Central tool registry - can be used as a singleton"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.tools = {}
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'ToolRegistry':
        """Get the global tool registry instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool:
        return self.tools.get(name)

    def get_tools_by_names(self, tool_names: List[str]) -> Dict[str, Tool]:
        """Return a dictionary of tools with the specified names"""
        tools_dict = {}
        for name in tool_names:
            if name in self.tools:
                tools_dict[name] = self.tools[name]
        return tools_dict

    def get_tools_for_provider(self, provider_name: str) -> List[Dict[str, Any]]:
        if provider_name.lower() == "openai":
            return [tool.to_openai_format() for tool in self.tools.values()]
        elif provider_name.lower() == "anthropic":
            return [tool.to_anthropic_format() for tool in self.tools.values()]
        else:
            return []  # xAI doesn't support tools

    def execute_tool(self, tool_call: Dict[str, Any], context: ToolExecutionContext) -> Any:
        """Execute a tool with context"""
        tool_name = tool_call["function"]["name"]
        tool = self.get_tool(tool_name)
        if tool:
            import json
            args = json.loads(tool_call["function"]["arguments"])
            return tool.execute(context, **args)
        return None


# Global tool registry instance
global_tool_registry = ToolRegistry.get_instance()