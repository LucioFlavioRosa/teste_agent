from typing import Optional, Dict, Any

from tools import github_reader
from tools.revisor_geral import executar_analise_llm

modelo_llm = 'gpt-4.1'
max_tokens_saida = 3000

analises_validas = ["design", "pentest", "seguranca", "terraform"]

def code_from_repo(repositorio: str, tipo_analise: str) -> Dict[str, str]:
    """
    Lê o código de um repositório GitHub para análise.

    Args:
        repositorio (str): Nome do repositório GitHub.
        tipo_analise (str): Tipo de análise a ser realizada.

    Returns:
        Dict[str, str]: Dicionário de arquivos e seus conteúdos.
    """
    try:
        print('Iniciando a leitura do repositório: ' + repositorio)
        codigo_para_analise = github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo_para_analise
    except Exception as e:
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e

def validar_entrada(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None) -> Any:
    """
    Valida os parâmetros de entrada para a análise.

    Args:
        tipo_analise (str): Tipo de análise a ser realizada.
        repositorio (Optional[str]): Nome do repositório GitHub.
        codigo (Optional[str]): Código fonte diretamente fornecido.

    Returns:
        Any: Código a ser analisado.
    """
    if tipo_analise not in analises_validas:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {analises_validas}")
    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")
    if codigo is None:
        codigo_para_analise = code_from_repo(tipo_analise=tipo_analise, repositorio=repositorio)
    else:
        codigo_para_analise = codigo
    return codigo_para_analise

def executar_analise(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[str] = None,
    instrucoes_extras: str = "",
    model_name: str = modelo_llm,
    max_token_out: int = max_tokens_saida
) -> Dict[str, Any]:
    """
    Orquestra a execução da análise LLM sobre o código fornecido.

    Args:
        tipo_analise (str): Tipo de análise a ser realizada.
        repositorio (Optional[str]): Nome do repositório GitHub.
        codigo (Optional[str]): Código fonte diretamente fornecido.
        instrucoes_extras (str): Instruções adicionais para a análise.
        model_name (str): Nome do modelo LLM a ser utilizado.
        max_token_out (int): Limite máximo de tokens na saída.

    Returns:
        Dict[str, Any]: Resultado da análise.
    """
    codigo_para_analise = validar_entrada(tipo_analise=tipo_analise, repositorio=repositorio, codigo=codigo)
    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
    resultado = executar_analise_llm(
        tipo_analise=tipo_analise,
        codigo=str(codigo_para_analise),
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}
