from typing import Optional, Dict, Any
from tools import github_reader
from tools.revisor_geral import executar_analise_llm
from tools.factory import AnaliseFactory
import logging

logger = logging.getLogger(__name__)

MODELO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000


def code_from_repo(repositorio: str, tipo_analise: str):
    """
    Obtém o código fonte do repositório para análise.
    """
    try:
        logger.info('Iniciando a leitura do repositório: %s', repositorio)
        codigo_para_analise = github_reader.main(
            repo=repositorio,
            tipo_de_analise=tipo_analise
        )
        return codigo_para_analise
    except Exception as e:
        logger.error("Falha ao executar a análise de '%s': %s", tipo_analise, e)
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e


def validation(tipo_analise: str,
               repositorio: Optional[str] = None,
               codigo: Optional[str] = None):
    """
    Valida os parâmetros de entrada para análise.
    """
    factory = AnaliseFactory()
    analises_validas = factory.tipos_disponiveis()

    if tipo_analise not in analises_validas:
        raise ValueError(
            f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {analises_validas}")

    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")

    if codigo is None:
        codigo_para_analise = code_from_repo(
            tipo_analise=tipo_analise,
            repositorio=repositorio
        )
    else:
        codigo_para_analise = codigo

    return codigo_para_analise


def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo: Optional[str] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    """
    Orquestra o fluxo de análise, delegando responsabilidades para módulos especializados.
    """
    codigo_para_analise = validation(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo=codigo
    )

    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}

    factory = AnaliseFactory()
    executor = factory.criar_executor(tipo_analise)

    resultado = executor.executar(
        codigo=str(codigo_para_analise),
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}
