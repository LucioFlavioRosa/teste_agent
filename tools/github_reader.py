"""
Módulo github_reader

Responsável por conectar-se ao GitHub, autenticar via token e extrair recursivamente arquivos de um repositório para análise, filtrando por extensões relevantes ao tipo de análise (ex: Python, Terraform, Docker, etc).

Funções principais:
- conection: Estabelece conexão autenticada com o GitHub.
- main: Ponto de entrada para extração de arquivos.

MAPEAMENTO_TIPO_EXTENSOES define os tipos de arquivos suportados por análise.
"""

import re
from github import Github
from github.Auth import Token
from google.colab import userdata
from typing import Dict, Optional, List

def conection(repositorio: str) -> 'github.Repository.Repository':
    """
    Estabelece conexão autenticada com o repositório GitHub informado.

    Args:
        repositorio (str): Nome do repositório no formato 'usuario/repositorio'.

    Returns:
        github.Repository.Repository: Objeto de repositório autenticado.

    Raises:
        Exception: Se o token não estiver disponível ou conexão falhar.

    Example:
        >>> repo = conection('usuario/repo')
    """
    GITHUB_TOKEN = userdata.get('github_token')
    auth = Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    return g.get_repo(repositorio)

MAPEAMENTO_TIPO_EXTENSOES: Dict[str, List[str]] = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}

def _leitura_recursiva_com_debug(
    repo: 'github.Repository.Repository',
    extensoes: Optional[List[str]],
    path: str = "",
    arquivos_do_repo: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    Lê recursivamente arquivos do repositório, filtrando por extensões.

    Args:
        repo (github.Repository.Repository): Objeto de repositório GitHub.
        extensoes (Optional[List[str]]): Lista de extensões de interesse.
        path (str): Caminho relativo inicial (default: raiz).
        arquivos_do_repo (Optional[Dict[str, str]]): Dicionário acumulador.

    Returns:
        Dict[str, str]: Dicionário de caminhos para conteúdos dos arquivos.

    Example:
        >>> _leitura_recursiva_com_debug(repo, ['.py'])
        {'app/main.py': '...'}
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
                        print(f"DEBUG: Erro ao decodificar '{conteudo.path}': {e}")
    except Exception as e:
        print(f"DEBUG: Erro ao acessar '{path}': {e}")
    return arquivos_do_repo

def main(repo: str, tipo_de_analise: str) -> Dict[str, str]:
    """
    Ponto de entrada para extração de arquivos do repositório GitHub.

    Args:
        repo (str): Nome do repositório (ex: 'usuario/repositorio').
        tipo_de_analise (str): Tipo de análise para filtrar extensões.

    Returns:
        Dict[str, str]: Dicionário de caminhos de arquivos para seus conteúdos.

    Raises:
        Exception: Se conexão ou leitura falhar.

    Example:
        >>> arquivos = main('usuario/repo', 'python')
        {'app/main.py': '...'}
    """
    repositorio_final = conection(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = _leitura_recursiva_com_debug(
        repositorio_final,
        extensoes=extensoes_alvo
    )
    return arquivos_encontrados
