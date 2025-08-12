from tools import github_reader

class GithubAdapter:
    """Adapter para abstrair a integração com o GitHub."""
    def obter_codigo(self, repo: str, tipo_de_analise: str):
        return github_reader.main(repo, tipo_de_analise)
