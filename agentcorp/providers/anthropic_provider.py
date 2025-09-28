from typing import List, Dict, Any
from .base import Provider, Message
import anthropic


class AnthropicProvider(Provider):
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        super().__init__(api_key, model)
        self.client = anthropic.Anthropic(api_key=api_key)

    def chat(self, messages: List[Message], **kwargs) -> str:
        # Convert to Anthropic format
        system_message = None
        anthropic_messages = []
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({"role": msg.role, "content": msg.content})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_message,
            messages=anthropic_messages,
            **kwargs
        )
        return response.content[0].text

    def supports_tools(self) -> bool:
        return True

    def chat_with_tools(self, messages: List[Message], tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        # Convert tools to Anthropic format
        anthropic_tools = []
        for tool in tools:
            anthropic_tools.append({
                "name": tool["function"]["name"],
                "description": tool["function"]["description"],
                "input_schema": tool["function"]["parameters"]
            })

        system_message = None
        anthropic_messages = []
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({"role": msg.role, "content": msg.content})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_message,
            messages=anthropic_messages,
            tools=anthropic_tools,
            **kwargs
        )

        result = {"content": "", "tool_calls": []}
        for content_block in response.content:
            if content_block.type == "text":
                result["content"] += content_block.text
            elif content_block.type == "tool_use":
                result["tool_calls"].append({
                    "id": content_block.id,
                    "function": {
                        "name": content_block.name,
                        "arguments": str(content_block.input)
                    }
                })
        return result