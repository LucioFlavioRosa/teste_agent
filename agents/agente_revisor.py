from typing import Optional, Dict, Any
from tools import github_reader
from tools.revisor_geral import executar_analise_llm
from tools.validator import validar_tipo_analise, validar_parametros_entrada
from tools.context import AnaliseContexto
import logging

modelo_llm = 'gpt-4.1'
max_tokens_saida = 3000
analises_validas = ["design", "pentest", "seguranca", "terraform"]

logger = logging.getLogger(__name__)


def obter_codigo_para_analise(repositorio: Optional[str], tipo_analise: str, codigo: Optional[str]) -> str:
    """
    Obtém o código a ser analisado, seja de um repositório remoto ou fornecido diretamente.
    """
    if codigo is not None:
        return codigo
    if repositorio is not None:
        logger.info(f'Iniciando a leitura do repositório: {repositorio}')
        return github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)
    raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")


def montar_contexto(tipo_analise: str, repositorio: Optional[str], codigo: Optional[str], instrucoes_extras: str, model_name: str, max_token_out: int) -> AnaliseContexto:
    """
    Cria um objeto de contexto para a análise.
    """
    return AnaliseContexto(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo=codigo,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )


def executar_analise(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[str] = None,
    instrucoes_extras: str = "",
    model_name: str = modelo_llm,
    max_token_out: int = max_tokens_saida
) -> Dict[str, Any]:
    """
    Orquestra a execução da análise, separando validação, obtenção de código e execução da LLM.
    """
    validar_tipo_analise(tipo_analise, analises_validas)
    validar_parametros_entrada(repositorio, codigo)
    contexto = montar_contexto(tipo_analise, repositorio, codigo, instrucoes_extras, model_name, max_token_out)
    try:
        codigo_para_analise = obter_codigo_para_analise(contexto.repositorio, contexto.tipo_analise, contexto.codigo)
    except Exception as e:
        logger.error(f"Falha ao obter código para análise: {e}")
        raise RuntimeError(f"Falha ao obter código para análise: {e}") from e

    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}

    try:
        resultado = executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=str(codigo_para_analise),
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        return {"tipo_analise": tipo_analise, "resultado": resultado}
    except Exception as e:
        logger.error(f"Falha ao executar análise LLM: {e}")
        raise RuntimeError(f"Falha ao executar análise LLM: {e}") from e
