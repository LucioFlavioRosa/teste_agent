import re
import logging
from github import Github
from github.Auth import Token
from google.colab import userdata


def obter_github_token():
    """
    Obtém o token do Github de forma centralizada.
    """
    return userdata.get('github_token')


def criar_github_client(token: str = None):
    """
    Cria um cliente Github, permitindo injeção para testes.
    """
    if token is None:
        token = obter_github_token()
    auth = Token(token)
    return Github(auth=auth)


def conection(repositorio: str, github_client=None):
    """
    Conecta ao repositório Github usando o cliente fornecido ou padrão.
    """
    if github_client is None:
        github_client = criar_github_client()
    return github_client.get_repo(repositorio)


MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}


def _leitura_recursiva_com_debug(repo, extensoes, path="", arquivos_do_repo=None):
    """
    Lê recursivamente arquivos do repositório, filtrando por extensões.
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
                        logging.warning(f"ERRO na decodificação de '{conteudo.path}': {e}")
    except Exception as e:
        logging.error(f"Erro ao ler conteúdo do repositório: {e}")
    return arquivos_do_repo


def main(repo, tipo_de_analise: str, github_client=None):
    """
    Função principal para leitura de arquivos de um repositório Github.
    """
    repositorio_final = conection(repositorio=repo, github_client=github_client)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = _leitura_recursiva_com_debug(repositorio_final, extensoes=extensoes_alvo)
    return arquivos_encontrados
