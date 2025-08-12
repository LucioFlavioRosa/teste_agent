import re
from github import Github
from github.Auth import Token
from google.colab import userdata


def conection(repositorio: str):
    """
    Estabelece conexão com o repositório Github usando token do Colab.
    Args:
        repositorio (str): Nome do repositório.
    Returns:
        github.Repository.Repository: Objeto de repositório Github.
    """
    GITHUB_TOKEN = userdata.get('github_token')
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

def _deve_ler_arquivo(conteudo, extensoes):
    """
    Decide se um arquivo deve ser lido, dado suas extensões.
    """
    if extensoes is None:
        return True
    return any(conteudo.path.endswith(ext) for ext in extensoes) or conteudo.name in extensoes

def _leitura_recursiva_com_debug(repo, extensoes, path="", arquivos_do_repo=None):
    """
    Lê recursivamente arquivos do repositório, filtrando pelas extensões.
    Args:
        repo: Objeto de repositório Github.
        extensoes (list): Lista de extensões alvo.
        path (str): Caminho atual.
        arquivos_do_repo (dict): Acumulador de arquivos.
    Returns:
        dict: Arquivos lidos.
    """
    if arquivos_do_repo is None:
        arquivos_do_repo = {}
    try:
        conteudos = repo.get_contents(path)
        for conteudo in conteudos:
            if conteudo.type == "dir":
                _leitura_recursiva_com_debug(repo, extensoes, conteudo.path, arquivos_do_repo)
            else:
                if _deve_ler_arquivo(conteudo, extensoes):
                    try:
                        codigo = conteudo.decoded_content.decode('utf-8')
                        arquivos_do_repo[conteudo.path] = codigo
                    except Exception as e:
                        print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")
    except Exception as e:
        print(e)
    return arquivos_do_repo

def main(repo, tipo_de_analise: str):
    """
    Função principal para leitura do repositório Github.
    Args:
        repo (str): Nome do repositório.
        tipo_de_analise (str): Tipo de análise.
    Returns:
        dict: Arquivos encontrados.
    """
    repositorio_final = conection(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = _leitura_recursiva_com_debug(
        repositorio_final, extensoes=extensoes_alvo)
    return arquivos_encontrados
