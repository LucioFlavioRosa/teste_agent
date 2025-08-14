from interfaces.code_source_interface import ICodeSource
from github import Github
from github.Auth import Token

class GitHubCodeSource(ICodeSource):
    """
    Implementação concreta de fonte de código para GitHub.
    Token e autenticação são injetados, não dependem mais de Colab ou variáveis globais.
    """
    def __init__(self, github_token: str):
        self.github_token = github_token

    def _connect(self, repositorio: str):
        auth = Token(self.github_token)
        g = Github(auth=auth)
        return g.get_repo(repositorio)

    def _recursive_read(self, repo, extensoes, path="", arquivos_do_repo=None):
        if arquivos_do_repo is None:
            arquivos_do_repo = {}
        try:
            conteudos = repo.get_contents(path)
            for conteudo in conteudos:
                if conteudo.type == "dir":
                    self._recursive_read(repo, extensoes, conteudo.path, arquivos_do_repo)
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

    def get_code(self, repo: str, tipo_analise: str):
        extensoes_alvo = self.get_extensions_for_analysis(tipo_analise)
        repositorio_final = self._connect(repositorio=repo)
        arquivos_encontrados = self._recursive_read(repositorio_final, extensoes=extensoes_alvo)
        return arquivos_encontrados

    def get_extensions_for_analysis(self, tipo_analise: str):
        # OCP: pode ser estendido por subclasse ou configuração externa
        mapping = {
            "terraform": [".tf", ".tfvars"],
            "python": [".py"],
            "cloudformation": [".json", ".yaml", ".yml"],
            "ansible": [".yml", ".yaml"],
            "docker": ["Dockerfile"]
        }
        return mapping.get(tipo_analise.lower())
