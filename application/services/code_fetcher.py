class CodeFetcher:
    def __init__(self, code_repository):
        self.code_repository = code_repository

    def fetch(self, source):
        if hasattr(source, 'repo_name'):
            return self.code_repository.fetch_files(source.file_filter)
        else:
            return source.code
