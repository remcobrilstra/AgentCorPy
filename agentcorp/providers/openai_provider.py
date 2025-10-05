from typing import List, Dict, Any
from .base import Provider, Message, retry_on_connection_error
from ..tool_registry import Tool
from ..models import ProviderResponse
import openai


class OpenAIProvider(Provider):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(api_key, model)
        self.client = openai.OpenAI(api_key=api_key)

    @retry_on_connection_error()
    def chat(self, messages: List[Message], **kwargs) -> ProviderResponse:
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
        content = response.choices[0].message.content or ""
        input_tokens = getattr(response.usage, 'prompt_tokens', 0)
        output_tokens = getattr(response.usage, 'completion_tokens', 0)
        return ProviderResponse(
            message=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            function_calls=[]
        )

    def supports_tools(self) -> bool:
        return True

    @retry_on_connection_error()
    def chat_with_tools(self, messages: List[Message], tools: List[Dict[str, Any]], **kwargs) -> ProviderResponse:
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
        content = message.content or ""
        input_tokens = getattr(response.usage, 'prompt_tokens', 0)
        output_tokens = getattr(response.usage, 'completion_tokens', 0)
        function_calls = []
        if message.tool_calls:
            function_calls = [
                {
                    "id": tool_call.id,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
                for tool_call in message.tool_calls
            ]
        return ProviderResponse(
            message=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            function_calls=function_calls
        )

    def get_tools_format(self, tools: Dict[str, Tool]) -> List[Dict[str, Any]]:
        return [tool.to_openai_format() for tool in tools.values()]