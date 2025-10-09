from typing import Dict, Any, List, Optional
from github import Github
from github.Auth import Token

class GitHubRepository:
    def __init__(self, config_provider):
        self.config_provider = config_provider
    def fetch_code(self, repo_name: str, filters: Dict[str, Any]) -> Dict[str, str]:
        token = self.config_provider.get_secret('github_token')
        auth = Token(token)
        github_client = Github(auth=auth)
        repo = github_client.get_repo(repo_name)
        extensions = filters.get('extensions')
        max_depth = filters.get('max_depth')
        max_workers = filters.get('max_workers', 4)
        arquivos_do_repo = {}
        caminhos_a_explorar = [('', 0)]
        while caminhos_a_explorar:
            caminho_atual, profundidade = caminhos_a_explorar.pop()
            if max_depth is not None and profundidade > max_depth:
                continue
            try:
                conteudos = repo.get_contents(caminho_atual)
            except Exception:
                continue
            for item in conteudos:
                if item.type == "dir":
                    caminhos_a_explorar.append((item.path, profundidade + 1))
                else:
                    if extensions is None or any(item.path.endswith(ext) or item.name == ext for ext in extensions):
                        try:
                            conteudo = item.decoded_content.decode('utf-8')
                            arquivos_do_repo[item.path] = conteudo
                        except Exception:
                            continue
        return arquivos_do_repo
    def is_available(self) -> bool:
        try:
            token = self.config_provider.get_secret('github_token')
            return bool(token)
        except Exception:
            return False
