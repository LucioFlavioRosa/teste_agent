from interfaces.code_source_interface import ICodeSource
from tools.github_reader import GitHubCodeSource

class CodeSourceFactory:
    """
    Factory para instanciar fontes de código conforme configuração.
    """
    @staticmethod
    def create(source_type: str, **kwargs) -> ICodeSource:
        if source_type == 'github':
            return GitHubCodeSource(kwargs['github_token'])
        raise ValueError(f"Tipo de fonte de código '{source_type}' não suportado.")
