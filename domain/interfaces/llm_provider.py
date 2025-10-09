from typing import Protocol, List, Dict

class ILLMProvider(Protocol):
    def generate_completion(self, messages: List[Dict], model: str, max_tokens: int) -> str:
        ...
    def is_configured(self) -> bool:
        ...
