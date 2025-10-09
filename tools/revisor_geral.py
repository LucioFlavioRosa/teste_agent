from infrastructure.di_container import DIContainer
from domain.models.analysis_request import AnalysisRequest
from domain.models.analysis_config import AnalysisConfig

def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int
) -> str:
    config = AnalysisConfig(
        model_name=model_name,
        max_tokens=max_token_out
    )
    request = AnalysisRequest(
        tipo_analise=tipo_analise,
        codigo=codigo,
        instrucoes_extras=analise_extra,
        config=config
    )
    container = DIContainer()
    result = container.analyze_code_use_case.execute(request)
    if not result.sucesso:
        raise RuntimeError(f'Erro ao executar análise: {result.erro}')
    return result.conteudo
