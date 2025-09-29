from typing import List, Dict, Any
from .providers import Message


class Memory:
    def __init__(self, max_messages: int = 100):
        self.messages: List[Message] = []
        self.max_messages = max_messages

    def add_message(self, role: str, content: str, tool_calls: List[Dict[str, Any]] = None, tool_call_id: str = None) -> Message:
        msg = Message(role, content, tool_calls, tool_call_id)
        self.messages.append(msg)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)  # Remove oldest
        return msg
    
    def remove_message(self, message: Message):
        if message in self.messages:
            self.messages.remove(message)

    def get_messages(self) -> List[Message]:
        return self.messages.copy()

    def clear(self):
        self.messages = []

    def set_system_prompt(self, prompt: str):
        # Remove existing system messages
        self.messages = [msg for msg in self.messages if msg.role != "system"]
        # Add new system message at the beginning
        self.messages.insert(0, Message("system", prompt))