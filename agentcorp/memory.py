from typing import List
from .providers import Message


class Memory:
    def __init__(self, max_messages: int = 100):
        self.messages: List[Message] = []
        self.max_messages = max_messages

    def add_message(self, role: str, content: str):
        self.messages.append(Message(role, content))
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)  # Remove oldest

    def get_messages(self) -> List[Message]:
        return self.messages.copy()

    def clear(self):
        self.messages = []

    def set_system_prompt(self, prompt: str):
        # Remove existing system messages
        self.messages = [msg for msg in self.messages if msg.role != "system"]
        # Add new system message at the beginning
        self.messages.insert(0, Message("system", prompt))