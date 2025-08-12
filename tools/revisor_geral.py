from typing import Dict
from tools.integracao_llm import LLMAnalyzer

def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int
) -> str:
    """
    Encapsula a chamada ao LLMAnalyzer para manter compatibilidade retroativa.
    """
    llm_analyzer = LLMAnalyzer()
    return llm_analyzer.executar_analise_llm(
        tipo_analise=tipo_analise,
        codigo=codigo,
        analise_extra=analise_extra,
        model_name=model_name,
        max_token_out=max_token_out
    )
