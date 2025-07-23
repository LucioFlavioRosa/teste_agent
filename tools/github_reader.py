import re
from github import Github
from github.Auth import Token
from google.colab import userdata
from typing import Dict, Optional, Any


def conectar_ao_github(repositorio: str) -> Any:
    """Adapter para conexão ao GitHub."""
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

def filtrar_arquivo_por_extensao(conteudo, extensoes):
    if extensoes is None:
        return True
    return any(conteudo.path.endswith(ext) for ext in extensoes) or conteudo.name in extensoes


def _leitura_recursiva_com_debug(repo, extensoes, path="", arquivos_do_repo=None):
    if arquivos_do_repo is None:
        arquivos_do_repo = {}
    try:
        conteudos = repo.get_contents(path)
        for conteudo in conteudos:
            if conteudo.type == "dir":
                _leitura_recursiva_com_debug(repo, extensoes, conteudo.path, arquivos_do_repo)
            else:
                if filtrar_arquivo_por_extensao(conteudo, extensoes):
                    try:
                        codigo = conteudo.decoded_content.decode('utf-8')
                        arquivos_do_repo[conteudo.path] = codigo
                    except Exception as e:
                        print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")
    except Exception as e:
        print(e)
    return arquivos_do_repo


def main(repo: str, tipo_de_analise: str) -> Dict[str, str]:
    """Função principal para obter código do GitHub, separando acesso e filtragem."""
    repositorio_final = conectar_ao_github(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = _leitura_recursiva_com_debug(repositorio_final,
                                                        extensoes=extensoes_alvo)
    return arquivos_encontrados
