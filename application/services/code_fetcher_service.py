class CodeFetcherService:
    def __init__(self, code_repository):
        self.code_repository = code_repository
    def fetch_from_repository(self, repo_name, analysis_type, extensions=None):
        filters = {'extensions': extensions}
        return self.code_repository.fetch_code(repo_name, filters)
    def prepare_code(self, code_input):
        if isinstance(code_input, dict):
            return '\n\n'.join(f"# Arquivo: {k}\n{v}" for k, v in code_input.items())
        return str(code_input)
