from abc import ABC, abstractmethod
from typing import Dict, Any


class IAnalysisExecutor(ABC):
    """Interface para execução de análises LLM."""
    
    @abstractmethod
    def execute_analysis(
        self,
        tipo_analise: str,
        codigo: str,
        analise_extra: str = "",
        model_name: str = "gpt-4.1",
        max_token_out: int = 3000
    ) -> str:
        """Executa análise LLM no código fornecido.
        
        Args:
            tipo_analise: Tipo de análise a executar
            codigo: Código a ser analisado
            analise_extra: Instruções extras para análise
            model_name: Nome do modelo LLM
            max_token_out: Máximo de tokens de saída
            
        Returns:
            Resultado da análise como string
        """
        pass
