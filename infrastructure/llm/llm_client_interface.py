from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ILLMClient(ABC):
    @abstractmethod
    def chat_completion(self, messages: List[Dict[str, Any]], model: str, temperature: float, max_tokens: int) -> str:
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        pass
