from typing import List, Dict, Any
from .base import Provider, Message, retry_on_connection_error
from ..tool_registry import Tool
import anthropic
import json


class AnthropicProvider(Provider):
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        super().__init__(api_key, model)
        self.client = anthropic.Anthropic(api_key=api_key)

    @retry_on_connection_error()
    def chat(self, messages: List[Message], **kwargs) -> Dict[str, Any]:
        # Convert to Anthropic format
        system_message = None
        anthropic_messages = []
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            elif msg.role == "tool":
                # For Anthropic, tool results are added as user messages with tool_result
                anthropic_messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_call_id": msg.tool_call_id,
                            "content": msg.content
                        }
                    ]
                })
            else:
                content = msg.content
                if msg.tool_calls:
                    # Anthropic doesn't use tool_calls in history like this, but for consistency
                    pass
                anthropic_messages.append({"role": msg.role, "content": content})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_message,
            messages=anthropic_messages,
            **kwargs
        )
        return {
            "content": response.content[0].text,
            "usage": response.usage
        }

    def supports_tools(self) -> bool:
        return True

    @retry_on_connection_error()
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
            elif msg.role == "tool":
                # Tool results
                anthropic_messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_call_id": msg.tool_call_id,
                            "content": msg.content
                        }
                    ]
                })
            else:
                content = msg.content
                if msg.tool_calls:
                    # For assistant messages with tool_calls, Anthropic expects tool_use in content
                    content_blocks = [{"type": "text", "text": content}]
                    for tc in msg.tool_calls:
                        content_blocks.append({
                            "type": "tool_use",
                            "id": tc["id"],
                            "name": tc["function"]["name"],
                            "input": json.loads(tc["function"]["arguments"])
                        })
                    anthropic_messages.append({"role": msg.role, "content": content_blocks})
                else:
                    anthropic_messages.append({"role": msg.role, "content": content})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_message,
            messages=anthropic_messages,
            tools=anthropic_tools,
            **kwargs
        )

        result = {"content": "", "tool_calls": [], "usage": response.usage}
        for content_block in response.content:
            if content_block.type == "text":
                result["content"] += content_block.text
            elif content_block.type == "tool_use":
                result["tool_calls"].append({
                    "id": content_block.id,
                    "function": {
                        "name": content_block.name,
                        "arguments": json.dumps(content_block.input)
                    }
                })
        return result

    def get_tools_format(self, tools: Dict[str, Tool]) -> List[Dict[str, Any]]:
        return [tool.to_anthropic_format() for tool in tools.values()]