import re
from github import Github
from github.Auth import Token
from google.colab import userdata
from typing import Dict, Optional, List


def conection(repositorio: str):
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

def _filtrar_extensao(conteudo, extensoes: Optional[List[str]]):
    if extensoes is None:
        return True
    return any(conteudo.path.endswith(ext) for ext in extensoes) or conteudo.name in extensoes

def _ler_arquivo(conteudo, arquivos_do_repo):
    try:
        codigo = conteudo.decoded_content.decode('utf-8')
        arquivos_do_repo[conteudo.path] = codigo
    except Exception as e:
        print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")

def _leitura_recursiva(repo, extensoes, path="", arquivos_do_repo=None):
    if arquivos_do_repo is None:
        arquivos_do_repo = {}
    try:
        conteudos = repo.get_contents(path)
        for conteudo in conteudos:
            if conteudo.type == "dir":
                _leitura_recursiva(repo, extensoes, conteudo.path, arquivos_do_repo)
            else:
                if _filtrar_extensao(conteudo, extensoes):
                    _ler_arquivo(conteudo, arquivos_do_repo)
    except Exception as e:
        print(e)
    return arquivos_do_repo

def main(repo, tipo_de_analise: str) -> Dict[str, str]:
    repositorio_final = conection(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = _leitura_recursiva(repositorio_final, extensoes=extensoes_alvo)
    return arquivos_encontrados
