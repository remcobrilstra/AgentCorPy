from typing import List, Dict, Any
from .providers import Message
from .models import get_model_info, ProviderResponse
import tiktoken
from .logging import logger


class Memory:
    def __init__(self, max_messages: int = 100, provider: str = "openai", model: str = "gpt-3.5-turbo"):
        self.messages: List[Message] = []
        self.max_messages = max_messages
        self.provider = provider
        self.model = model
        model_info = get_model_info(provider, model)
        self.input_cost_per_million = model_info["input_cost"]
        self.output_cost_per_million = model_info["output_cost"]
        self.max_tokens = model_info["context_size"]
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def add_message(self, role: str, content: str, tool_calls: List[Dict[str, Any]] = None, tool_call_id: str = None, task_id: str = None) -> Message:
        msg = Message(role, content, tool_calls, tool_call_id)
        msg.task_id = task_id
        # Estimate input tokens
        try:
            encoding = tiktoken.encoding_for_model(self.model)
            msg.input_tokens_estimate = len(encoding.encode(content)) + (len(tool_calls) * 10 if tool_calls else 0)
        except Exception as e:
            msg.input_tokens_estimate = int(len(content.split()) * 1.3)
            # logger.warning(f"Token estimation failed for model {self.model}: {e}")
        
        self.messages.append(msg)
        
        # Prune if exceeding limits
        while len(self.messages) > self.max_messages or self.total_input_tokens + msg.input_tokens_estimate > self.max_tokens:
            removed = self.messages.pop(0)
            self.total_input_tokens -= getattr(removed, 'input_tokens', 0)
        
        return msg
    
    def add_response_message(self, role: str, response: ProviderResponse, tool_call_id: str = None, task_id: str = None) -> Message:
        msg = self.add_message(role, response.message, response.function_calls, tool_call_id, task_id)
        # Adjust input_tokens: subtract estimated, add actual

        msg.input_tokens_total = response.input_tokens
        msg.input_tokens = response.input_tokens - self.total_input_tokens
        self.total_input_tokens = self.total_input_tokens + response.input_tokens
        msg.output_tokens = response.output_tokens
        self.total_output_tokens += response.output_tokens
        return msg
    
    def get_total_cost(self) -> float:
        input_cost = (self.total_input_tokens / 1_000_000) * self.input_cost_per_million
        output_cost = (self.total_output_tokens / 1_000_000) * self.output_cost_per_million
        return input_cost + output_cost
    
    def get_total_tokens_used(self) -> int:
        return self.total_input_tokens + self.total_output_tokens
    
    def get_message_cost(self, message: Message) -> float:
        input_cost = (getattr(message, 'input_tokens', 0) / 1_000_000) * self.input_cost_per_million
        output_cost = (getattr(message, 'output_tokens', 0) / 1_000_000) * self.output_cost_per_million
        return input_cost + output_cost
    
    def get_messages_for_task(self, task_id: str) -> List[Message]:
        return [msg for msg in self.messages if getattr(msg, 'task_id', None) == task_id or msg.role == "system"]
    
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
        # Add new system message at the beginning with efficiency guidelines
        full_prompt = f"{prompt}"#\n\nGuidelines: Minimize steps to solve tasks efficiently. Decompose complex tasks into subtasks. Avoid redundant messages to conserve tokens."
        self.messages.insert(0, Message("system", full_prompt))