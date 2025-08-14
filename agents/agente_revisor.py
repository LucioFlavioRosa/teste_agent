"""
Módulo agente_revisor

Este módulo orquestra a análise de código-fonte de repositórios GitHub utilizando ferramentas de leitura e integração com LLM (OpenAI). Suporta múltiplos tipos de análise (design, pentest, segurança, terraform) e pode operar tanto sobre código extraído de repositórios quanto sobre código fornecido diretamente.

Dependências:
- tools/github_reader.py: Extração recursiva de código do GitHub.
- tools/revisor_geral.py: Interface com LLM para análise.

Fluxo principal:
1. Validação do tipo de análise e origem do código.
2. Extração do código (se necessário).
3. Chamada ao analisador LLM.

Exemplo de uso:
    resultado = main(tipo_analise='design', repositorio='usuario/repo')
"""

from typing import Optional, Dict, Any
from tools import github_reader
from tools.revisor_geral import executar_analise_llm

modelo_llm = 'gpt-4.1'
max_tokens_saida = 3000

analises_validas = ["design", "pentest", "seguranca", "terraform"]

def code_from_repo(repositorio: str, tipo_analise: str) -> Dict[str, str]:
    """
    Extrai o código-fonte de um repositório GitHub para análise.

    Args:
        repositorio (str): Nome do repositório no formato 'usuario/repositorio'.
        tipo_analise (str): Tipo de análise a ser realizada (ex: 'design', 'pentest').

    Returns:
        Dict[str, str]: Dicionário mapeando caminhos de arquivos para seus conteúdos.

    Raises:
        RuntimeError: Se houver falha na leitura do repositório.

    Example:
        >>> code_from_repo('usuario/repo', 'design')
        {'app/main.py': '...'}
    """
    try:
        print('Iniciando a leitura do repositório: ' + repositorio)
        codigo_extraido_para_analise = github_reader.main(
            repo=repositorio,
            tipo_de_analise=tipo_analise
        )
        return codigo_extraido_para_analise
    except Exception as e:
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e

def validation(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    Valida os parâmetros de entrada e obtém o código para análise.

    Args:
        tipo_analise (str): Tipo de análise a ser realizada.
        repositorio (Optional[str]): Nome do repositório GitHub.
        codigo (Optional[Dict[str, str]]): Código-fonte fornecido diretamente.

    Returns:
        Dict[str, str]: Código-fonte a ser analisado.

    Raises:
        ValueError: Se parâmetros obrigatórios estiverem ausentes ou inválidos.

    Example:
        >>> validation('design', repositorio='usuario/repo')
        {'app/main.py': '...'}
    """
    if tipo_analise not in analises_validas:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {analises_validas}")
    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")
    if codigo is None:
        codigo_extraido_para_analise = code_from_repo(
            tipo_analise=tipo_analise,
            repositorio=repositorio
        )
    else:
        codigo_extraido_para_analise = codigo
    return codigo_extraido_para_analise

def main(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[Dict[str, str]] = None,
    instrucoes_extras: str = "",
    model_name: str = modelo_llm,
    max_token_out: int = max_tokens_saida
) -> Dict[str, Any]:
    """
    Função principal para executar a análise de código via LLM.

    Args:
        tipo_analise (str): Tipo de análise ('design', 'pentest', etc).
        repositorio (Optional[str]): Nome do repositório GitHub.
        codigo (Optional[Dict[str, str]]): Código-fonte fornecido diretamente.
        instrucoes_extras (str): Instruções adicionais para a análise.
        model_name (str): Nome do modelo LLM a ser utilizado.
        max_token_out (int): Limite máximo de tokens para a resposta.

    Returns:
        Dict[str, Any]: Resultado da análise, incluindo tipo e resposta do LLM.

    Example:
        >>> main('design', repositorio='usuario/repo')
        {'tipo_analise': 'design', 'resultado': '...'}
    """
    codigo_para_analise = validation(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo=codigo
    )
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

# Alias para compatibilidade com código legado
executar_analise = main
