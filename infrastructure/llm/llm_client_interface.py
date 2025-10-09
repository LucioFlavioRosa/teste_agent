from abc import ABC, abstractmethod

class ILLMClient(ABC):
    @abstractmethod
    def chat_completion(self, messages, model, temperature, max_tokens):
        pass

    @abstractmethod
    def validate_connection(self):
        pass
