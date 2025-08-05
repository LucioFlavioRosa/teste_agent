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


class GithubRepoReader:
    """
    Adaptador para leitura de código em repositórios GitHub, permitindo injeção de autenticação.
    """
    def __init__(self, github_token=None, github_client=None):
        self.github_token = github_token or userdata.get('github_token')
        self.auth = Token(self.github_token)
        self.github_client = github_client or Github(auth=self.auth)

    def conection(self, repositorio: str):
        return self.github_client.get_repo(repositorio)

    def _leitura_recursiva_com_debug(self, repo, extensoes, path="", arquivos_do_repo=None):
        if arquivos_do_repo is None:
            arquivos_do_repo = {}
        try:
            conteudos = repo.get_contents(path)
            for conteudo in conteudos:
                if conteudo.type == "dir":
                    self._leitura_recursiva_com_debug(repo, extensoes, conteudo.path, arquivos_do_repo)
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
                            print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")
        except Exception as e:
            print(e)
        return arquivos_do_repo

    def ler_codigo(self, repo: str, tipo_de_analise: str):
        repositorio_final = self.conection(repositorio=repo)
        extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
        arquivos_encontrados = self._leitura_recursiva_com_debug(repositorio_final, extensoes=extensoes_alvo)
        return arquivos_encontrados
