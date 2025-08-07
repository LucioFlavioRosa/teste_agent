from github import Github
from github.Auth import Token
from google.colab import userdata
from typing import Optional, Dict, Any, List


DEFAULT_MAPPINGS = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}


class GitHubRepositoryReader:
    """
    Classe para leitura de repositórios GitHub, separando conexão, leitura e filtragem.
    """
    def __init__(self, github_token: Optional[str] = None, ext_mapping: Optional[Dict[str, List[str]]] = None):
        self.github_token = github_token or userdata.get('github_token')
        self.ext_mapping = ext_mapping or DEFAULT_MAPPINGS

    def connect(self, repositorio: str) -> Any:
        auth = Token(self.github_token)
        g = Github(auth=auth)
        return g.get_repo(repositorio)

    def _recursive_read(self, repo, extensoes: Optional[List[str]], path: str = "", arquivos_do_repo: Optional[Dict[str, str]] = None) -> Dict[str, str]:
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

    def read_repository(self, repo: str, tipo_de_analise: str) -> Dict[str, str]:
        repositorio_final = self.connect(repositorio=repo)
        extensoes_alvo = self.ext_mapping.get(tipo_de_analise.lower())
        arquivos_encontrados = self._recursive_read(repositorio_final, extensoes=extensoes_alvo)
        return arquivos_encontrados
