from typing import List, Dict, Any
from .base import Provider, Message
import openai


class OpenAIProvider(Provider):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(api_key, model)
        self.client = openai.OpenAI(api_key=api_key)

    def chat(self, messages: List[Message], **kwargs) -> str:
        openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            **kwargs
        )
        return response.choices[0].message.content

    def supports_tools(self) -> bool:
        return True

    def chat_with_tools(self, messages: List[Message], tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            tools=tools,
            tool_choice="auto",
            **kwargs
        )
        message = response.choices[0].message
        result = {"content": message.content, "tool_calls": []}
        if message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
                for tool_call in message.tool_calls
            ]
        return result