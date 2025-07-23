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


def obter_extensoes_por_tipo(tipo_de_analise: str, mapeamento: Optional[Dict[str, List[str]]] = None) -> Optional[List[str]]:
    """
    Permite extensão do mapeamento de tipos/extensões sem modificar o código-fonte.
    """
    if mapeamento is None:
        mapeamento = {
            "terraform": [".tf", ".tfvars"],
            "python": [".py"],
            "cloudformation": [".json", ".yaml", ".yml"],
            "ansible": [".yml", ".yaml"],
            "docker": ["Dockerfile"],
        }
    return mapeamento.get(tipo_de_analise.lower())


def filtrar_extensao(conteudo_path: str, extensoes: Optional[List[str]]) -> bool:
    """
    Função separada para filtrar arquivos por extensão ou nome.
    """
    if extensoes is None:
        return True
    return any(conteudo_path.endswith(ext) for ext in extensoes) or any(ext == conteudo_path.split('/')[-1] for ext in extensoes)


def leitura_recursiva(repo, extensoes, path="", arquivos_do_repo=None):
    """
    Função recursiva para leitura de arquivos, separando logging e filtragem.
    """
    if arquivos_do_repo is None:
        arquivos_do_repo = {}
    try:
        conteudos = repo.get_contents(path)
        for conteudo in conteudos:
            if conteudo.type == "dir":
                leitura_recursiva(repo, extensoes, conteudo.path, arquivos_do_repo)
            else:
                if filtrar_extensao(conteudo.path, extensoes):
                    try:
                        codigo = conteudo.decoded_content.decode('utf-8')
                        arquivos_do_repo[conteudo.path] = codigo
                    except Exception as e:
                        print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")
    except Exception as e:
        print(e)
    return arquivos_do_repo


def main(repo, tipo_de_analise: str, mapeamento: Optional[Dict[str, List[str]]] = None):
    repositorio_final = conection(repositorio=repo)
    extensoes_alvo = obter_extensoes_por_tipo(tipo_de_analise, mapeamento)
    arquivos_encontrados = leitura_recursiva(repositorio_final, extensoes=extensoes_alvo)
    return arquivos_encontrados
