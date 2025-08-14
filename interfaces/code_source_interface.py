from abc import ABC, abstractmethod

class ICodeSource(ABC):
    """
    Interface para fontes de código (ex: GitHub, GitLab, local).
    """
    @abstractmethod
    def get_code(self, repo: str, tipo_analise: str):
        pass
