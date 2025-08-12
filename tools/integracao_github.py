from tools import github_reader

class GithubCodeProvider:
    """
    Abstrai o acesso ao código-fonte do GitHub e permite fácil mock para testes.
    """
    def get_code(self, repo: str, tipo_de_analise: str):
        return github_reader.main(repo, tipo_de_analise)
