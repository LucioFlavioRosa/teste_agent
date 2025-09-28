from abc import ABC, abstractmethod

class CredentialsProviderInterface(ABC):
    @abstractmethod
    def get_openai_api_key(self) -> str:
        pass