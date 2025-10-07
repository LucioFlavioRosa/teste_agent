from typing import Optional
from agents.interfaces import ICodeReader
from tools import github_reader


class GitHubCodeReader(ICodeReader):
    """Implementação concreta para leitura de código do GitHub."""
    
    def read_code(self, repositorio: str, tipo_analise: str) -> str:
        """Lê código de um repositório GitHub.
        
        Args:
            repositorio: Nome do repositório GitHub
            tipo_analise: Tipo de análise a ser executada
            
        Returns:
            Código lido do repositório
            
        Raises:
            RuntimeError: Se falhar ao ler o repositório
        """
        try:
            print(f'Iniciando a leitura do repositório: {repositorio}')
            codigo_para_analise = github_reader.main(
                repo=repositorio,
                tipo_de_analise=tipo_analise
            )
            return codigo_para_analise
        except Exception as e:
            raise RuntimeError(
                f"Falha ao executar a análise de '{tipo_analise}': {e}"
            ) from e
