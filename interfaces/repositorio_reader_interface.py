from abc import ABC, abstractmethod
from typing import Dict, Optional

class IRepositorioReader(ABC):
    """Interface para leitores de repositório"""
    
    @abstractmethod
    def obter_arquivos_para_analise(self, repo_nome: str, tipo_analise: str, 
                                   max_workers: int = 4, 
                                   max_depth: Optional[int] = None) -> Dict[str, str]:
        """Obtém arquivos do repositório para análise"""
        pass