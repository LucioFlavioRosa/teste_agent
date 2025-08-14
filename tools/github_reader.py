"""
Módulo utilitário para leitura recursiva de repositórios GitHub.

Permite extrair arquivos de código relevantes para diferentes tipos de análise (Terraform, Python, etc.).
Requer autenticação via token GitHub.
"""
import re
from github import Github
from github.Auth import Token
from google.colab import userdata
from typing import Optional, Dict, Any, List

def conection(repositorio: str) -> Any:
    """
    Estabelece conexão autenticada com um repositório GitHub.

    Args:
        repositorio (str): Nome do repositório no formato 'usuario/repositorio'.

    Returns:
        github.Repository.Repository: Objeto de repositório GitHub.

    Raises:
        RuntimeError: Se o token não estiver disponível ou a conexão falhar.

    Example:
        >>> repo = conection('usuario/repo')
    """
    GITHUB_TOKEN = userdata.get('github_token')
    if not GITHUB_TOKEN:
        raise RuntimeError("Token do GitHub não encontrado em 'userdata'.")
    auth = Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    return g.get_repo(repositorio)

MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}

def _leitura_recursiva_com_debug(
    repo: Any,
    extensoes: Optional[List[str]],
    path: str = "",
    arquivos_do_repo: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    Lê recursivamente arquivos do repositório, filtrando por extensão.

    Args:
        repo (github.Repository.Repository): Objeto de repositório GitHub.
        extensoes (Optional[List[str]]): Lista de extensões ou nomes de arquivos alvo.
        path (str): Caminho relativo inicial.
        arquivos_do_repo (Optional[Dict[str, str]]): Acumulador de arquivos lidos.

    Returns:
        Dict[str, str]: Dicionário de caminhos para conteúdos dos arquivos.

    Example:
        >>> _leitura_recursiva_com_debug(repo, ['.py'])
        {'src/main.py': '...'}
    """
    if arquivos_do_repo is None:
        arquivos_do_repo = {}
    try:
        conteudos = repo.get_contents(path)
        for conteudo in conteudos:
            if conteudo.type == "dir":
                _leitura_recursiva_com_debug(repo, extensoes, conteudo.path, arquivos_do_repo)
            else:
                ler_o_arquivo = False
                if extensoes is None:
                    ler_o_arquivo = True
                else:
                    if any(conteudo.path.endswith(ext) for ext in extensoes) or conteudo.name in extensoes:
                        ler_o_arquivo = True
                if ler_o_arquivo:
                    try:
                        codigo = conteudo.decoded_content.decode('utf-8')
                        arquivos_do_repo[conteudo.path] = codigo
                    except Exception as e:
                        print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")
    except Exception as e:
        print(e)
    return arquivos_do_repo

def main(repo: str, tipo_de_analise: str) -> Dict[str, str]:
    """
    Função principal para leitura de arquivos de um repositório GitHub.

    Args:
        repo (str): Nome do repositório no formato 'usuario/repositorio'.
        tipo_de_analise (str): Tipo da análise para filtrar extensões.

    Returns:
        Dict[str, str]: Dicionário de arquivos relevantes.

    Example:
        >>> main('usuario/repo', 'python')
        {'src/main.py': '...'}
    """
    repositorio_final = conection(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = _leitura_recursiva_com_debug(
        repositorio_final,
        extensoes=extensoes_alvo
    )
    return arquivos_encontrados
