class AnalysisOrchestrator:
    def __init__(self, code_fetcher_service, llm_provider, prompt_loader):
        self.code_fetcher_service = code_fetcher_service
        self.llm_provider = llm_provider
        self.prompt_loader = prompt_loader
    def execute_analysis(self, request):
        prompt = self.prompt_loader.load_prompt(request.analysis_type)
        if isinstance(request.code_source, dict):
            code = self.code_fetcher_service.prepare_code(request.code_source)
        else:
            code = str(request.code_source)
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": code},
            {"role": "user", "content": f'Instruções extras do usuário a serem consideradas na análise: {request.extra_instructions}' if request.extra_instructions.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
        ]
        result = self.llm_provider.generate_completion(messages, request.model_name, request.max_tokens)
        return type('AnalysisResult', (), {})(request.analysis_type, result, {})
