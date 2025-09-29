from typing import List, Dict, Any
import requests
from .base import Provider, Message
from ..tool_registry import Tool


class XAIProvider(Provider):
    def __init__(self, api_key: str, model: str = "grok-beta"):
        super().__init__(api_key, model)
        self.base_url = "https://api.x.ai/v1"

    def chat(self, messages: List[Message], **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        xai_messages = []
        for msg in messages:
            msg_dict = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                msg_dict["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                msg_dict["tool_call_id"] = msg.tool_call_id
            xai_messages.append(msg_dict)

        data = {
            "model": self.model,
            "messages": xai_messages,
            **kwargs
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        )

        if response.status_code != 200:
            raise Exception(f"xAI API error: {response.status_code} - {response.text}")

        result = response.json()
        return result["choices"][0]["message"]["content"]

    def supports_tools(self) -> bool:
        return True  # Assuming xAI supports tools

    def chat_with_tools(self, messages: List[Message], tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        xai_messages = []
        for msg in messages:
            msg_dict = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                msg_dict["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                msg_dict["tool_call_id"] = msg.tool_call_id
            xai_messages.append(msg_dict)

        data = {
            "model": self.model,
            "messages": xai_messages,
            **kwargs
        }

        if tools:
            data["tools"] = tools
            data["tool_choice"] = "auto"

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        )

        if response.status_code != 200:
            raise Exception(f"xAI API error: {response.status_code} - {response.text}")

        result = response.json()
        message = result["choices"][0]["message"]
        response_dict = {"content": message.get("content", ""), "tool_calls": []}
        if "tool_calls" in message:
            response_dict["tool_calls"] = [
                {
                    "id": tc["id"],
                    "function": {
                        "name": tc["function"]["name"],
                        "arguments": tc["function"]["arguments"]
                    }
                }
                for tc in message["tool_calls"]
            ]
        return response_dict

    def get_tools_format(self, tools: Dict[str, Tool]) -> List[Dict[str, Any]]:
        return [tool.to_openai_format() for tool in tools.values()]