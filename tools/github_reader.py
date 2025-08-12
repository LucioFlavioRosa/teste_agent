import re
from github import Github
from github.Auth import Token
from google.colab import userdata
import logging

logger = logging.getLogger(__name__)


def get_github_token():
    """Obtém o token do Github de forma desacoplada."""
    return userdata.get('github_token')


def autenticar_github(token: str):
    """Autentica no Github usando o token fornecido."""
    auth = Token(token)
    return Github(auth=auth)


def conection(repositorio: str):
    """Retorna objeto de repositório autenticado."""
    token = get_github_token()
    if not token:
        logger.error("Token do Github não encontrado.")
        raise ValueError("Token do Github não encontrado.")
    g = autenticar_github(token)
    return g.get_repo(repositorio)


MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}


def filtrar_extensao(conteudo, extensoes):
    """Decide se deve ler o arquivo pelo nome/extensão."""
    if extensoes is None:
        return True
    return any(conteudo.path.endswith(ext) for ext in extensoes) or conteudo.name in extensoes


def _leitura_recursiva(repo, extensoes, path="", arquivos_do_repo=None):
    """
    Lê arquivos recursivamente do repositório Github, filtrando por extensão.
    """
    if arquivos_do_repo is None:
        arquivos_do_repo = {}
    try:
        conteudos = repo.get_contents(path)
        for conteudo in conteudos:
            if conteudo.type == "dir":
                _leitura_recursiva(repo, extensoes, conteudo.path, arquivos_do_repo)
            else:
                if filtrar_extensao(conteudo, extensoes):
                    try:
                        codigo = conteudo.decoded_content.decode('utf-8')
                        arquivos_do_repo[conteudo.path] = codigo
                    except Exception as e:
                        logger.warning("Erro na decodificação de '%s': %s", conteudo.path, e)
    except Exception as e:
        logger.error("Erro ao ler conteúdo do repositório: %s", e)
    return arquivos_do_repo


def main(repo, tipo_de_analise: str):
    """
    Interface principal para leitura de arquivos do repositório Github.
    """
    repositorio_final = conection(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = _leitura_recursiva(
        repositorio_final,
        extensoes=extensoes_alvo
    )
    return arquivos_encontrados
