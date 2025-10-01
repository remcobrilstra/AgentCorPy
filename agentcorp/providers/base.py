from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..tool_registry import Tool
import time
import logging

logger = logging.getLogger(__name__)


def retry_on_connection_error(max_retries=1, backoff_factor=1.0):
    """
    Decorator to retry API calls on connection errors with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts (default: 1)
        backoff_factor: Backoff multiplier for exponential backoff (default: 1.0)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, TimeoutError, OSError) as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = backoff_factor * (2 ** attempt)
                        logger.warning(f"Connection error on attempt {attempt + 1}, retrying in {wait_time:.1f}s: {e}")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Connection error on final attempt {attempt + 1}: {e}")
                except Exception as e:
                    # For non-connection errors, don't retry
                    raise e
            
            # If we get here, all retries failed
            raise last_exception
        return wrapper
    return decorator


class Message:
    def __init__(self, role: str, content: str, tool_calls: List[Dict[str, Any]] = None, tool_call_id: str = None):
        self.role = role
        self.content = content
        self.tool_calls = tool_calls or []
        self.tool_call_id = tool_call_id
        self.visible = True  # For future use
        self.input_tokens = 0
        self.output_tokens = 0
        self.task_id = None


class Provider(ABC):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def chat(self, messages: List[Message], **kwargs) -> Dict[str, Any]:
        """Send a chat request and return the response with content and usage"""
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