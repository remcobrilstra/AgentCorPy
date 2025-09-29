from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..tool_registry import Tool


class Message:
    def __init__(self, role: str, content: str, tool_calls: List[Dict[str, Any]] = None, tool_call_id: str = None):
        self.role = role
        self.content = content
        self.tool_calls = tool_calls or []
        self.tool_call_id = tool_call_id
        self.visible = True  # For future use


class Provider(ABC):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def chat(self, messages: List[Message], **kwargs) -> str:
        """Send a chat request and return the response"""
        pass

    @abstractmethod
    def supports_tools(self) -> bool:
        """Check if the provider supports tool calling"""
        pass

    @abstractmethod
    def chat_with_tools(self, messages: List[Message], tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Send a chat request with tools and return response with tool calls"""
        pass

    @abstractmethod
    def get_tools_format(self, tools: Dict[str, Tool]) -> List[Dict[str, Any]]:
        """Convert tools to provider-specific format"""
        pass