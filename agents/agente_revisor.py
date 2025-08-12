from typing import Optional, Dict, Any

from tools import github_reader
from tools.revisor_geral import executar_analise_llm

MODELO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000

ANALISES_VALIDAS = ["design", "pentest", "seguranca", "terraform"]

def obter_codigo_do_repositorio(repositorio: str, tipo_analise: str, leitor_repo=github_reader.main):
    """
    Obtém o código do repositório para análise.
    Args:
        repositorio (str): Nome do repositório.
        tipo_analise (str): Tipo de análise a ser realizada.
        leitor_repo (callable): Função para leitura do repositório.
    Returns:
        dict: Código do repositório.
    """
    try:
        print(f'Iniciando a leitura do repositório: {repositorio}')
        codigo_para_analise = leitor_repo(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo_para_analise
    except Exception as e:
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e

def validar_parametros(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None):
    """
    Valida os parâmetros de entrada para análise.
    Args:
        tipo_analise (str): Tipo de análise.
        repositorio (Optional[str]): Nome do repositório.
        codigo (Optional[str]): Código fornecido.
    Returns:
        dict: Código para análise.
    Raises:
        ValueError: Se parâmetros inválidos forem fornecidos.
    """
    if tipo_analise not in ANALISES_VALIDAS:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {ANALISES_VALIDAS}")
    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")
    return None

def preparar_codigo_para_analise(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None, leitor_repo=github_reader.main):
    """
    Orquestra a obtenção do código para análise.
    Args:
        tipo_analise (str): Tipo de análise.
        repositorio (Optional[str]): Nome do repositório.
        codigo (Optional[str]): Código fornecido.
        leitor_repo (callable): Função para leitura do repositório.
    Returns:
        dict/str: Código para análise.
    """
    validar_parametros(tipo_analise, repositorio, codigo)
    if codigo is not None:
        return codigo
    return obter_codigo_do_repositorio(repositorio, tipo_analise, leitor_repo=leitor_repo)

def executar_analise(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[str] = None,
    instrucoes_extras: str = "",
    model_name: str = MODELO_LLM,
    max_token_out: int = MAX_TOKENS_SAIDA,
    leitor_repo=github_reader.main,
    executor_llm=executar_analise_llm
) -> Dict[str, Any]:
    """
    Executa a análise do código usando o modelo LLM.
    Args:
        tipo_analise (str): Tipo de análise.
        repositorio (Optional[str]): Nome do repositório.
        codigo (Optional[str]): Código fornecido.
        instrucoes_extras (str): Instruções adicionais.
        model_name (str): Nome do modelo LLM.
        max_token_out (int): Máximo de tokens de saída.
        leitor_repo (callable): Função para leitura do repositório.
        executor_llm (callable): Função para executar análise LLM.
    Returns:
        dict: Resultado da análise.
    """
    codigo_para_analise = preparar_codigo_para_analise(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo=codigo,
        leitor_repo=leitor_repo
    )
    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
    resultado = executor_llm(
        tipo_analise=tipo_analise,
        codigo=str(codigo_para_analise),
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}
