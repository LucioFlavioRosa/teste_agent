from domain.models.analysis_result import AnalysisResult

class AnalysisOrchestrator:
    def __init__(self, llm_provider, code_repository, prompt_loader):
        self.llm_provider = llm_provider
        self.code_repository = code_repository
        self.prompt_loader = prompt_loader

    def execute(self, request):
        prompt = self.prompt_loader.load(request.analysis_type)
        if hasattr(request.code_source, 'repo_name'):
            code_files = self.code_repository.fetch_files(request.code_source.file_filter)
        else:
            code_files = request.code_source.code
        if isinstance(code_files, dict):
            code_str = '\n\n'.join(f"# Arquivo: {k}\n{v}" for k, v in code_files.items())
        else:
            code_str = str(code_files)
        result_content = self.llm_provider.analyze(prompt, code_str)
        metadata = {"analysis_type": request.analysis_type}
        return AnalysisResult(request.analysis_type, result_content, metadata)
