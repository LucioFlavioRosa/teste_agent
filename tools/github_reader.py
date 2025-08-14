"""
Módulo github_reader

Utilitário para leitura recursiva de arquivos de repositórios GitHub, filtrando por extensões relevantes para diferentes tipos de análise (terraform, python, cloudformation, ansible, docker).
"""
import re
from github import Github
from github.Auth import Token
from google.colab import userdata

def conection(repositorio: str) -> Github:
    """
    Realiza a conexão autenticada com o repositório GitHub.

    Args:
        repositorio (str): Nome do repositório no formato 'usuario/repositorio'.

    Returns:
        Github: Objeto de repositório autenticado.

    Raises:
        RuntimeError: Se o token de autenticação não estiver disponível.
    """
    GITHUB_TOKEN = userdata.get('github_token')
    if not GITHUB_TOKEN:
        raise RuntimeError("Token do GitHub não encontrado na configuração do Colab.")
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
    repo: Github, 
    extensoes: list, 
    path: str = "", 
    arquivos_do_repo: dict = None
) -> dict:
    """
    Lê recursivamente os arquivos do repositório, filtrando por extensões.

    Args:
        repo (Github): Objeto de repositório autenticado.
        extensoes (list): Lista de extensões ou nomes de arquivos a serem lidos.
        path (str): Caminho relativo para início da leitura.
        arquivos_do_repo (dict): Dicionário acumulador dos arquivos lidos.

    Returns:
        dict: Dicionário {caminho_arquivo: conteudo}.

    Raises:
        Exception: Se ocorrer erro de leitura ou decodificação de arquivos.
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
                        # Erro de decodificação é logado para debug, mas não interrompe a leitura dos demais arquivos.
                        print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")
    except Exception as e:
        print(e)
    return arquivos_do_repo

def main(repo: str, tipo_de_analise: str) -> dict:
    """
    Função principal para leitura de arquivos de um repositório GitHub, filtrando por tipo de análise.

    Args:
        repo (str): Nome do repositório no formato 'usuario/repositorio'.
        tipo_de_analise (str): Tipo de análise desejada (ex: 'terraform', 'python').

    Returns:
        dict: Dicionário {caminho_arquivo: conteudo} dos arquivos relevantes.

    Example:
        >>> main('usuario/projeto', 'python')
        {'src/main.py': 'conteudo...', ...}
    """
    repositorio_final = conection(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = _leitura_recursiva_com_debug(
        repositorio_final, 
        extensoes=extensoes_alvo
    )
    return arquivos_encontrados
