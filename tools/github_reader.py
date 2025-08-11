from github import Github
from github.Auth import Token
from google.colab import userdata

class GitHubRepositoryAdapter:
    """
    Adapter para leitura de repositórios GitHub.
    """
    def __init__(self, repositorio: str):
        self.repositorio = repositorio
        self.client = self._connect()

    def _connect(self):
        github_token = userdata.get('github_token')
        auth = Token(github_token)
        g = Github(auth=auth)
        return g.get_repo(self.repositorio)

    def list_files(self, extensoes, path="", arquivos_do_repo=None):
        if arquivos_do_repo is None:
            arquivos_do_repo = {}
        try:
            conteudos = self.client.get_contents(path)
            for conteudo in conteudos:
                if conteudo.type == "dir":
                    self.list_files(extensoes, conteudo.path, arquivos_do_repo)
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

MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}

def main(repo, tipo_de_analise: str):
    adapter = GitHubRepositoryAdapter(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = adapter.list_files(extensoes=extensoes_alvo)
    return arquivos_encontrados
