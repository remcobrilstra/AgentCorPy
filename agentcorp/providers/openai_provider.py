from typing import List, Dict, Any
from .base import Provider, Message, retry_on_connection_error
from ..tool_registry import Tool
import openai


class OpenAIProvider(Provider):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(api_key, model)
        self.client = openai.OpenAI(api_key=api_key)

    @retry_on_connection_error()
    def chat(self, messages: List[Message], **kwargs) -> Dict[str, Any]:
        openai_messages = []
        for msg in messages:
            msg_dict = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                msg_dict["tool_calls"] = [
                    {
                        "id": tc["id"],
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"]
                        }
                    } for tc in msg.tool_calls
                ]
            if msg.tool_call_id:
                msg_dict["tool_call_id"] = msg.tool_call_id
            openai_messages.append(msg_dict)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            **kwargs
        )
        return {
            "content": response.choices[0].message.content,
            "usage": response.usage
        }

    def supports_tools(self) -> bool:
        return True

    @retry_on_connection_error()
    def chat_with_tools(self, messages: List[Message], tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        openai_messages = []
        for msg in messages:
            msg_dict = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                msg_dict["tool_calls"] = [
                    {
                        "id": tc["id"],
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"]
                        }
                    } for tc in msg.tool_calls
                ]
            if msg.tool_call_id:
                msg_dict["tool_call_id"] = msg.tool_call_id
            openai_messages.append(msg_dict)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            tools=tools,
            tool_choice="auto",
            **kwargs
        )
        message = response.choices[0].message
        result = {"content": message.content, "tool_calls": [], "usage": response.usage}
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

    def get_tools_format(self, tools: Dict[str, Tool]) -> List[Dict[str, Any]]:
        return [tool.to_openai_format() for tool in tools.values()]