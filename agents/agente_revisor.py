from typing import Optional, Dict, Any
from tools import github_reader
from tools.revisor_geral import executar_analise_llm

MODELO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000

ANALISES_VALIDAS = ["design", "pentest", "seguranca", "terraform"]


def code_from_repo(repositorio: str, tipo_analise: str, github_reader_func=github_reader.main):
    """
    Lê o código do repositório usando o reader fornecido.
    Args:
        repositorio (str): Nome do repositório.
        tipo_analise (str): Tipo de análise.
        github_reader_func (callable): Função de leitura do GitHub.
    Returns:
        dict: Código extraído do repositório.
    """
    try:
        codigo_para_analise = github_reader_func(
            repo=repositorio,
            tipo_de_analise=tipo_analise
        )
        return codigo_para_analise
    except Exception as exc:
        raise RuntimeError(
            f"Falha ao executar a análise de '{tipo_analise}': {exc}") from exc


def validation(tipo_analise: str,
               repositorio: Optional[str] = None,
               codigo: Optional[str] = None,
               github_reader_func=github_reader.main):
    """
    Valida os parâmetros de entrada para a análise.
    Args:
        tipo_analise (str): Tipo de análise.
        repositorio (str, opcional): Nome do repositório.
        codigo (str, opcional): Código em string.
        github_reader_func (callable): Função de leitura do GitHub.
    Returns:
        dict: Código para análise.
    """
    if tipo_analise not in ANALISES_VALIDAS:
        raise ValueError(
            f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {ANALISES_VALIDAS}")

    if repositorio is None and codigo is None:
        raise ValueError(
            "Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")

    if codigo is None:
        codigo_para_analise = code_from_repo(
            tipo_analise=tipo_analise,
            repositorio=repositorio,
            github_reader_func=github_reader_func
        )
    else:
        codigo_para_analise = codigo

    return codigo_para_analise


def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo: Optional[str] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA,
                     github_reader_func=github_reader.main,
                     executar_analise_llm_func=executar_analise_llm) -> Dict[str, Any]:
    """
    Orquestra a execução da análise, separando responsabilidades.
    Args:
        tipo_analise (str): Tipo de análise.
        repositorio (str, opcional): Nome do repositório.
        codigo (str, opcional): Código em string.
        instrucoes_extras (str): Instruções extras.
        model_name (str): Nome do modelo LLM.
        max_token_out (int): Máximo de tokens de saída.
        github_reader_func (callable): Função de leitura do GitHub.
        executar_analise_llm_func (callable): Função de execução da LLM.
    Returns:
        dict: Resultado da análise.
    """
    codigo_para_analise = validation(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo=codigo,
        github_reader_func=github_reader_func
    )

    if not codigo_para_analise:
        return {
            "tipo_analise": tipo_analise,
            "resultado": 'Não foi fornecido nenhum código para análise'
        }

    resultado = executar_analise_llm_func(
        tipo_analise=tipo_analise,
        codigo=str(codigo_para_analise),
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}
