from typing import Optional, Dict, Any
from tools import github_reader
from tools.revisor_geral import executar_analise_llm


MODELO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000
ANALISES_VALIDAS = [
    "design",
    "pentest",
    "seguranca",
    "terraform"
]

def code_from_repo(repositorio: str, tipo_analise: str, github_reader_mod=github_reader):
    """
    Lê o código de um repositório remoto usando o github_reader.
    Args:
        repositorio (str): Nome do repositório GitHub.
        tipo_analise (str): Tipo de análise a ser realizada.
        github_reader_mod: Módulo github_reader (injeção para testes).
    Returns:
        dict: Código para análise.
    """
    try:
        # Logging pode ser adicionado aqui no futuro
        codigo_para_analise = github_reader_mod.main(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo_para_analise
    except Exception as e:
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e

def validar_parametros(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None):
    """
    Valida os parâmetros de entrada para a análise.
    Args:
        tipo_analise (str): Tipo de análise.
        repositorio (str, opcional): Nome do repositório.
        codigo (str, opcional): Código fonte fornecido.
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

def obter_codigo_para_analise(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None, github_reader_mod=github_reader):
    """
    Orquestra a obtenção do código a ser analisado.
    """
    validar_parametros(tipo_analise=tipo_analise, repositorio=repositorio, codigo=codigo)
    if codigo is not None:
        return codigo
    return code_from_repo(tipo_analise=tipo_analise, repositorio=repositorio, github_reader_mod=github_reader_mod)

def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo: Optional[str] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA,
                     executar_analise_llm_func=executar_analise_llm,
                     github_reader_mod=github_reader) -> Dict[str, Any]:
    """
    Função principal para orquestrar a análise de código.
    Args:
        tipo_analise (str): Tipo de análise.
        repositorio (str, opcional): Repositório GitHub.
        codigo (str, opcional): Código fonte.
        instrucoes_extras (str): Instruções extras para análise.
        model_name (str): Nome do modelo LLM.
        max_token_out (int): Máximo de tokens de saída.
        executar_analise_llm_func: Função de análise LLM (injeção para testes).
        github_reader_mod: Módulo github_reader (injeção para testes).
    Returns:
        dict: Resultado da análise.
    """
    codigo_para_analise = obter_codigo_para_analise(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo=codigo,
        github_reader_mod=github_reader_mod
    )
    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
    resultado = executar_analise_llm_func(
        tipo_analise=tipo_analise,
        codigo=str(codigo_para_analise),
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}
