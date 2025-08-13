from typing import Optional, Dict, Any
from agents.strategies import AnalysisStrategyFactory, AnalysisType
from agents.dependencies import GithubReader, LLMClient


def main(tipo_analise: str,
         repositorio: Optional[str] = None,
         codigo: Optional[str] = None,
         instrucoes_extras: str = "",
         model_name: str = None,
         max_token_out: int = None,
         github_reader: GithubReader = None,
         llm_client: LLMClient = None) -> Dict[str, Any]:
    """
    Função principal de orquestração para análise de código.
    Separa responsabilidades de validação, leitura e execução de análise.
    """
    if github_reader is None:
        github_reader = GithubReader()
    if llm_client is None:
        llm_client = LLMClient()

    try:
        analysis_type = AnalysisType.from_str(tipo_analise)
    except ValueError as e:
        return {"tipo_analise": tipo_analise, "resultado": str(e)}

    if not repositorio and not codigo:
        return {"tipo_analise": tipo_analise, "resultado": "É obrigatório fornecer 'repositorio' ou 'codigo'."}

    if codigo is None:
        try:
            codigo_para_analise = github_reader.read_code(
                repositorio=repositorio,
                tipo_analise=analysis_type.value
            )
        except Exception as e:
            return {"tipo_analise": tipo_analise, "resultado": f"Falha ao ler repositório: {e}"}
    else:
        codigo_para_analise = codigo

    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}

    strategy = AnalysisStrategyFactory.get_strategy(
        analysis_type,
        llm_client=llm_client,
        model_name=model_name,
        max_token_out=max_token_out
    )
    resultado = strategy.execute(
        codigo=str(codigo_para_analise),
        analise_extra=instrucoes_extras
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}
