import re
from github import Github
from github.Auth import Token
from tools.secrets_provider import obter_github_token
import logging

logger = logging.getLogger(__name__)

MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}

def conection(repositorio: str):
    GITHUB_TOKEN = obter_github_token()
    auth = Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    return g.get_repo(repositorio)

def _leitura_recursiva(repo, extensoes, path="", arquivos_do_repo=None):
    """
    Lê recursivamente arquivos do repositório, filtrando por extensão.
    """
    if arquivos_do_repo is None:
        arquivos_do_repo = {}
    try:
        conteudos = repo.get_contents(path)
        for conteudo in conteudos:
            if conteudo.type == "dir":
                _leitura_recursiva(repo, extensoes, conteudo.path, arquivos_do_repo)
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
                        logger.warning(f"Erro na decodificação de '{conteudo.path}': {e}")
    except Exception as e:
        logger.error(f"Erro ao ler conteúdo do repositório: {e}")
    return arquivos_do_repo

def main(repo, tipo_de_analise: str):
    repositorio_final = conection(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = _leitura_recursiva(repositorio_final, extensoes=extensoes_alvo)
    return arquivos_encontrados
