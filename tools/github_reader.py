import re
from github import Github
from github.Auth import Token
from google.colab import userdata


MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}


def obter_token_github():
    """Obtém o token do GitHub de forma desacoplada."""
    return userdata.get('github_token')


def filtrar_arquivo_por_extensao(nome_arquivo, extensoes):
    if extensoes is None:
        return True
    return any(nome_arquivo.endswith(ext) for ext in extensoes) or nome_arquivo in extensoes


def decodificar_conteudo(conteudo):
    try:
        return conteudo.decoded_content.decode('utf-8')
    except Exception as e:
        print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")
        return None


def leitura_recursiva(repo, extensoes, path="", arquivos_do_repo=None):
    if arquivos_do_repo is None:
        arquivos_do_repo = {}
    try:
        conteudos = repo.get_contents(path)
        for conteudo in conteudos:
            if conteudo.type == "dir":
                leitura_recursiva(repo, extensoes, conteudo.path, arquivos_do_repo)
            else:
                if filtrar_arquivo_por_extensao(conteudo.path, extensoes):
                    codigo = decodificar_conteudo(conteudo)
                    if codigo is not None:
                        arquivos_do_repo[conteudo.path] = codigo
    except Exception as e:
        print(e)
    return arquivos_do_repo


class GithubRepoReader:
    """Adapter para leitura de repositórios GitHub."""
    def __init__(self, token=None):
        self.token = token or obter_token_github()
        if not self.token:
            raise ValueError("Token do GitHub não encontrado.")
        self.auth = Token(self.token)
        self.client = Github(auth=self.auth)

    def get_repo(self, repositorio):
        return self.client.get_repo(repositorio)

    def ler_codigo(self, repo, tipo_de_analise):
        repositorio_final = self.get_repo(repo)
        extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
        return leitura_recursiva(repositorio_final, extensoes=extensoes_alvo)
