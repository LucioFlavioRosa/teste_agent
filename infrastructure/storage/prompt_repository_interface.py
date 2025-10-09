from abc import ABC, abstractmethod

class IPromptRepository(ABC):
    @abstractmethod
    def get_prompt(self, tipo_analise: str) -> str:
        pass
