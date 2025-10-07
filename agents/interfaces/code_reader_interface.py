from abc import ABC, abstractmethod
from typing import Optional


class ICodeReader(ABC):
    """Interface para leitura de código de diferentes fontes."""
    
    @abstractmethod
    def read_code(self, repositorio: str, tipo_analise: str) -> str:
        """Lê código de um repositório para análise.
        
        Args:
            repositorio: Identificador do repositório
            tipo_analise: Tipo de análise a ser executada
            
        Returns:
            Código lido como string
            
        Raises:
            RuntimeError: Se falhar ao ler o código
        """
        pass
