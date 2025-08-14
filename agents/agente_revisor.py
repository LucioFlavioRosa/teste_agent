"""
Agente Revisor: Orquestra a análise automatizada de código-fonte utilizando ferramentas de leitura de repositórios GitHub e LLMs.

Expõe funções para validação de parâmetros, obtenção de código de repositórios e execução de análises técnicas (design, pentest, segurança, terraform).
"""

from typing import Optional, Dict, Any
from tools import github_reader
from tools.revisor_geral import executar_analise_llm

modelo_llm = 'gpt-4.1'
max_tokens_saida = 3000

analises_validas = ["design", "pentest", "seguranca", "terraform"]

def code_from_repo(repositorio: str, tipo_analise: str) -> Dict[str, str]:
    """
    Obtém o código-fonte de um repositório GitHub para análise, filtrando pelos tipos de arquivo relevantes.

    Args:
        repositorio (str): Nome do repositório no formato 'usuario/repositorio'.
        tipo_analise (str): Tipo de análise desejada ('design', 'pentest', etc).

    Returns:
        Dict[str, str]: Dicionário onde as chaves são caminhos de arquivos e os valores, seus conteúdos.

    Raises:
        RuntimeError: Se ocorrer qualquer erro ao acessar ou ler o repositório.

    Example:
        >>> code_from_repo('usuario/projeto', 'pentest')
        {'app/main.py': '...código...', ...}
    """
    try:
        print('Iniciando a leitura do repositório: ' + repositorio)
        codigo_para_analise = github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo_para_analise
    except Exception as e:
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e

def validation(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None) -> Dict[str, str]:
    """
    Valida os parâmetros de entrada e obtém o código-fonte a ser analisado.

    Args:
        tipo_analise (str): Tipo de análise desejada.
        repositorio (Optional[str]): Nome do repositório GitHub.
        codigo (Optional[str]): Código-fonte fornecido diretamente.

    Returns:
        Dict[str, str]: Código-fonte a ser analisado.

    Raises:
        ValueError: Se parâmetros obrigatórios estiverem ausentes ou inválidos.

    Example:
        >>> validation('pentest', repositorio='usuario/projeto')
        {'app/main.py': '...código...', ...}
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
    Executa a análise técnica do código-fonte utilizando LLM, retornando o resultado estruturado.

    Args:
        tipo_analise (str): Tipo de análise ('design', 'pentest', etc).
        repositorio (Optional[str]): Nome do repositório GitHub.
        codigo (Optional[str]): Código-fonte fornecido diretamente.
        instrucoes_extras (str): Instruções adicionais para a análise.
        model_name (str): Nome do modelo LLM a ser utilizado.
        max_token_out (int): Limite de tokens para a resposta do modelo.

    Returns:
        Dict[str, Any]: Resultado da análise, incluindo tipo e resposta do LLM.

    Example:
        >>> main('pentest', repositorio='usuario/projeto')
        {'tipo_analise': 'pentest', 'resultado': '...'}
    """
    codigo_para_analise = validation(tipo_analise=tipo_analise, repositorio=repositorio, codigo=codigo)
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
