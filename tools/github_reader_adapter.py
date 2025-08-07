from tools import github_reader

class GithubRepoReader:
    """
    Adapter para leitura de repositório GitHub, facilitando mock e testes.
    """
    def get_code(self, repo: str, tipo_de_analise: str):
        return github_reader.main(repo, tipo_de_analise)
