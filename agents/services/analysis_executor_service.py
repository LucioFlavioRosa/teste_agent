from agents.interfaces import IAnalysisExecutor
from tools.revisor_geral import executar_analise_llm


class LLMAnalysisExecutor(IAnalysisExecutor):
    """Implementação concreta para execução de análises LLM."""
    
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
            Resultado da análise
        """
        return executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=codigo,
            analise_extra=analise_extra,
            model_name=model_name,
            max_token_out=max_token_out
        )
