import re
from github import Github
from github.Auth import Token
from google.colab import userdata


class GithubRepositorioLeitor:
    """
    Interface para leitura de arquivos de um repositório Github.
    """
    MAPEAMENTO_TIPO_EXTENSOES = {
        "terraform": [".tf", ".tfvars"],
        "python": [".py"],
        "cloudformation": [".json", ".yaml", ".yml"],
        "ansible": [".yml", ".yaml"],
        "docker": ["Dockerfile"],
    }

    def __init__(self, token=None):
        self.token = token or userdata.get('github_token')
        self.auth = Token(self.token)
        self.github = Github(auth=self.auth)

    def conectar(self, repositorio: str):
        return self.github.get_repo(repositorio)

    def leitura_recursiva(self, repo, extensoes, path="", arquivos_do_repo=None):
        if arquivos_do_repo is None:
            arquivos_do_repo = {}
        try:
            conteudos = repo.get_contents(path)
            for conteudo in conteudos:
                if conteudo.type == "dir":
                    self.leitura_recursiva(repo, extensoes, conteudo.path, arquivos_do_repo)
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

    def ler_arquivos(self, repositorio: str, tipo_de_analise: str):
        repo = self.conectar(repositorio)
        extensoes_alvo = self.MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
        return self.leitura_recursiva(repo, extensoes=extensoes_alvo)

# Interface procedural para compatibilidade retroativa
leitor_padrao = GithubRepositorioLeitor()

def main(repo, tipo_de_analise: str):
    return leitor_padrao.ler_arquivos(repositorio=repo, tipo_de_analise=tipo_de_analise)
