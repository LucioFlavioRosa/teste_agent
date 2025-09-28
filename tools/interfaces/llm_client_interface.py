from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMClientInterface(ABC):
    @abstractmethod
    def chat_completion(self, messages: List[Dict[str, str]], model_name: str, max_tokens: int) -> str:
        pass