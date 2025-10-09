from infrastructure.llm.openai_client_adapter import OpenAIClientAdapter
from infrastructure.config.api_key_provider import ColabAPIKeyProvider, EnvironmentAPIKeyProvider
from services.prompt_loader_service import PromptLoaderService
from services.code_analysis_service import CodeAnalysisService
from application.use_cases.analyze_code_use_case import AnalyzeCodeUseCase

class DIContainer:
    def __init__(self, use_colab=True):
        if use_colab:
            self.api_key_provider = ColabAPIKeyProvider()
        else:
            self.api_key_provider = EnvironmentAPIKeyProvider()
        self.prompt_loader_service = PromptLoaderService()
        api_key = self.api_key_provider.get_api_key('openai')
        self.llm_client = OpenAIClientAdapter(api_key)
        self.code_analysis_service = CodeAnalysisService(self.llm_client, self.prompt_loader_service)
        self.analyze_code_use_case = AnalyzeCodeUseCase(self.code_analysis_service)
