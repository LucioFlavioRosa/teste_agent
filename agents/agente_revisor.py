"""
Agente de revisão de código-fonte para análise automatizada via LLM.

Este módulo oferece funções para coletar código de repositórios, validar parâmetros de análise e executar revisões técnicas usando modelos de linguagem.

Dependências:
- tools.github_reader
- tools.revisor_geral

Exemplo de uso:
    resultado = main(tipo_analise='pentest', repositorio='usuario/repositorio')
    print(resultado['resultado'])
"""
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
        repositorio (str): Nome do repositório no formato 'usuario/repositorio'.
        tipo_analise (str): Tipo da análise desejada (ex: 'pentest').

    Returns:
        Dict[str, str]: Dicionário com caminhos de arquivos como chaves e conteúdos como valores.

    Raises:
        RuntimeError: Se houver falha ao acessar ou ler o repositório.

    Example:
        >>> code_from_repo('usuario/repo', 'pentest')
        {'app/main.py': '...'}
    """
    try:
        print(f'Iniciando a leitura do repositório: {repositorio}')
        codigo_para_analise = github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo_para_analise
    except Exception as e:
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e

def validate_analysis_inputs(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None) -> Dict[str, str]:
    """
    Valida os parâmetros de entrada para análise e obtém o código-fonte.

    Args:
        tipo_analise (str): Tipo da análise ('design', 'pentest', etc.).
        repositorio (Optional[str]): Nome do repositório GitHub.
        codigo (Optional[str]): Código-fonte fornecido diretamente.

    Returns:
        Dict[str, str]: Código a ser analisado (dicionário de arquivos).

    Raises:
        ValueError: Se parâmetros obrigatórios estiverem ausentes ou inválidos.

    Example:
        >>> validate_analysis_inputs('pentest', repositorio='usuario/repo')
        {'app/main.py': '...'}
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

def main(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[str] = None,
    instrucoes_extras: str = "",
    model_name: str = modelo_llm,
    max_token_out: int = max_tokens_saida
) -> Dict[str, Any]:
    """
    Executa a análise do código-fonte usando LLM conforme o tipo especificado.

    Args:
        tipo_analise (str): Tipo da análise ('design', 'pentest', etc.).
        repositorio (Optional[str]): Nome do repositório GitHub.
        codigo (Optional[str]): Código-fonte fornecido diretamente.
        instrucoes_extras (str): Instruções adicionais para a análise.
        model_name (str): Nome do modelo LLM a ser utilizado.
        max_token_out (int): Limite de tokens para a resposta.

    Returns:
        Dict[str, Any]: Resultado da análise, incluindo tipo e resposta do LLM.

    Example:
        >>> main('pentest', repositorio='usuario/repo')
        {'tipo_analise': 'pentest', 'resultado': '...'}
    """
    codigo_para_analise = validate_analysis_inputs(tipo_analise=tipo_analise, repositorio=repositorio, codigo=codigo)
    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
    else:
        resultado = executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=str(codigo_para_analise),
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        return {"tipo_analise": tipo_analise, "resultado": resultado}

# Alias para compatibilidade retroativa
executar_analise = main
