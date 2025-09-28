from typing import List, Dict, Any
from .base import Provider, Message
import xai


class XAIProvider(Provider):
    def __init__(self, api_key: str, model: str = "grok-beta"):
        super().__init__(api_key, model)
        self.client = xai.Client(api_key=api_key)

    def chat(self, messages: List[Message], **kwargs) -> str:
        xai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=xai_messages,
            **kwargs
        )
        return response.choices[0].message.content

    def supports_tools(self) -> bool:
        return False  # Assuming xAI doesn't support tools yet

    def chat_with_tools(self, messages: List[Message], tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        # xAI may not support tools, so fall back to regular chat
        content = self.chat(messages, **kwargs)
        return {"content": content, "tool_calls": []}