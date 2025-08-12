import re
from github import Github
from github.Auth import Token
from google.colab import userdata
from typing import Optional, Dict

def conectar_github(repositorio: str) -> object:
    """
    Realiza a conexão com o GitHub usando token do Colab.
    """
    github_token = userdata.get('github_token')
    auth = Token(github_token)
    g = Github(auth=auth)
    return g.get_repo(repositorio)

MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}

def filtrar_extensao_arquivo(nome_arquivo: str, extensoes: Optional[list]) -> bool:
    """
    Decide se o arquivo deve ser lido baseado em suas extensões.
    """
    if extensoes is None:
        return True
    return any(nome_arquivo.endswith(ext) for ext in extensoes) or nome_arquivo in extensoes

def leitura_recursiva(repo, extensoes: Optional[list], path: str = "", arquivos_do_repo: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Lê recursivamente arquivos do repositório, filtrando pelas extensões.
    """
    if arquivos_do_repo is None:
        arquivos_do_repo = {}
    try:
        conteudos = repo.get_contents(path)
        for conteudo in conteudos:
            if conteudo.type == "dir":
                leitura_recursiva(repo, extensoes, conteudo.path, arquivos_do_repo)
            else:
                if filtrar_extensao_arquivo(conteudo.path, extensoes):
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
    Conecta ao repositório e retorna arquivos filtrados conforme o tipo de análise.
    """
    repositorio_final = conectar_github(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = leitura_recursiva(
        repositorio_final,
        extensoes=extensoes_alvo
    )
    return arquivos_encontrados
