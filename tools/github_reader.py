import re
from github import Github
from github.Auth import Token
from google.colab import userdata


class GithubRepositoryReader:
    """
    Classe responsável por abstrair acesso ao repositório Github e leitura dos arquivos.
    Permite substituição de implementação para facilitar testes e manutenção.
    """
    MAPEAMENTO_TIPO_EXTENSOES = {
        "terraform": [".tf", ".tfvars"],
        "python": [".py"],
        "cloudformation": [".json", ".yaml", ".yml"],
        "ansible": [".yml", ".yaml"],
        "docker": ["Dockerfile"],
    }

    def __init__(self, github_token=None):
        self.github_token = github_token or userdata.get('github_token')

    def conection(self, repositorio: str):
        if not self.github_token:
            raise ValueError("Token do Github não foi encontrado.")
        auth = Token(self.github_token)
        g = Github(auth=auth)
        return g.get_repo(repositorio)

    def _leitura_recursiva(self, repo, extensoes, path="", arquivos_do_repo=None):
        if arquivos_do_repo is None:
            arquivos_do_repo = {}
        try:
            conteudos = repo.get_contents(path)
            for conteudo in conteudos:
                if conteudo.type == "dir":
                    self._leitura_recursiva(repo, extensoes, conteudo.path, arquivos_do_repo)
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

    def main(self, repo, tipo_de_analise: str):
        repositorio_final = self.conection(repositorio=repo)
        extensoes_alvo = self.MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
        arquivos_encontrados = self._leitura_recursiva(repositorio_final, extensoes=extensoes_alvo)
        return arquivos_encontrados
