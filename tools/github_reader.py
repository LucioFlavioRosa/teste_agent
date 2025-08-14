"""
Utilitário para leitura recursiva de arquivos de um repositório GitHub, filtrando por extensões relevantes para diferentes tipos de análise (terraform, python, cloudformation, ansible, docker).

Fornece funções para conectar ao GitHub, ler arquivos recursivamente e retornar um dicionário de arquivos e seus conteúdos.
"""

import re
from github import Github
from github.Auth import Token
from google.colab import userdata
from typing import Dict, Optional, List

def conection(repositorio: str) -> Github:
    """
    Estabelece conexão autenticada com o repositório GitHub informado.

    Args:
        repositorio (str): Nome do repositório no formato 'usuario/repositorio'.

    Returns:
        Github: Objeto de repositório autenticado.

    Raises:
        Exception: Se o token não estiver disponível ou conexão falhar.

    Example:
        >>> repo = conection('usuario/projeto')
    """
    GITHUB_TOKEN = userdata.get('github_token')
    auth = Token(GITHUB_TOKEN)
    github_instance = Github(auth=auth)
    return github_instance.get_repo(repositorio)

MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}

def _leitura_recursiva_com_debug(
    repo,
    extensoes: Optional[List[str]],
    path: str = "",
    arquivos_do_repo: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    Lê recursivamente todos os arquivos do repositório, filtrando pelas extensões desejadas.
    Armazena os arquivos encontrados em um dicionário.

    Args:
        repo: Objeto de repositório GitHub autenticado.
        extensoes (Optional[List[str]]): Lista de extensões de arquivo a serem lidas.
        path (str): Caminho relativo dentro do repositório.
        arquivos_do_repo (Optional[Dict[str, str]]): Dicionário acumulador dos arquivos lidos.

    Returns:
        Dict[str, str]: Dicionário de caminhos de arquivos e seus conteúdos.

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
                # Recursão para subdiretórios
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
                        # Erro de decodificação pode ocorrer para arquivos binários ou corrompidos
                        print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")
    except Exception as e:
        # Pode ocorrer erro de permissão ou path inexistente
        print(e)
    return arquivos_do_repo

def main(repo: str, tipo_de_analise: str) -> Dict[str, str]:
    """
    Função principal para leitura de arquivos de um repositório GitHub, filtrando por tipo de análise.

    Args:
        repo (str): Nome do repositório no formato 'usuario/repositorio'.
        tipo_de_analise (str): Tipo de análise desejada ('terraform', 'python', etc).

    Returns:
        Dict[str, str]: Dicionário de caminhos de arquivos e seus conteúdos.

    Raises:
        Exception: Se a conexão ou leitura falhar.

    Example:
        >>> main('usuario/projeto', 'python')
        {'app/main.py': '...'}
    """
    repositorio_final = conection(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = _leitura_recursiva_com_debug(
        repositorio_final,
        extensoes=extensoes_alvo
    )
    return arquivos_encontrados
