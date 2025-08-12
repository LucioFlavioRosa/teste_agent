from typing import Optional, Dict, Any
import logging
from tools import github_reader
from tools.revisor_geral import executar_analise_llm


MODELO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000

ANALISES_VALIDAS = ["design", "pentest", "seguranca", "terraform"]


def obter_codigo_do_repositorio(repositorio: str, tipo_analise: str, github_client=None):
    """
    Lê o código do repositório para análise, utilizando o github_reader.
    """
    try:
        logging.info(f'Iniciando a leitura do repositório: {repositorio}')
        return github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise, github_client=github_client)
    except Exception as e:
        logging.error(f"Falha ao executar a análise de '{tipo_analise}': {e}")
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e


def validar_parametros(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None):
    """
    Valida os parâmetros de entrada para a análise.
    """
    if tipo_analise not in ANALISES_VALIDAS:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {ANALISES_VALIDAS}")

    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")


def preparar_codigo_para_analise(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None, github_client=None):
    """
    Prepara o código a ser analisado, seja lendo do repo ou usando o código fornecido.
    """
    validar_parametros(tipo_analise, repositorio, codigo)
    if codigo is not None:
        return codigo
    return obter_codigo_do_repositorio(repositorio, tipo_analise, github_client=github_client)


def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo: Optional[str] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA,
                     openai_client=None,
                     github_client=None) -> Dict[str, Any]:
    """
    Orquestra o fluxo de análise, preparando o código e delegando ao executor LLM.
    """
    try:
        codigo_para_analise = preparar_codigo_para_analise(tipo_analise=tipo_analise,
                                                           repositorio=repositorio,
                                                           codigo=codigo,
                                                           github_client=github_client)
    except Exception as e:
        logging.error(f"Erro ao preparar código para análise: {e}")
        return {"tipo_analise": tipo_analise, "resultado": f'Erro ao preparar código: {e}'}

    if not codigo_para_analise:
        logging.warning("Nenhum código fornecido para análise.")
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}

    try:
        resultado = executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=str(codigo_para_analise),
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out,
            openai_client=openai_client
        )
        return {"tipo_analise": tipo_analise, "resultado": resultado}
    except Exception as e:
        logging.error(f"Erro durante execução da análise LLM: {e}")
        return {"tipo_analise": tipo_analise, "resultado": f'Erro ao executar análise LLM: {e}'}
