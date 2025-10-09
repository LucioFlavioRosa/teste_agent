from abc import ABC, abstractmethod
from typing import Any, List, Dict

class LLMClientInterface(ABC):
    @abstractmethod
    def chat_completion(self, messages: List[Dict[str, Any]], model: str, temperature: float, max_tokens: int, **kwargs) -> Dict[str, Any]:
        pass
