from abc import ABC, abstractmethod

class SecretsManager(ABC):
    @abstractmethod
    def get_secret(self, key: str) -> str:
        pass
