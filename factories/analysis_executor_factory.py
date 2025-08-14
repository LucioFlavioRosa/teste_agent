from interfaces.analysis_executor_interface import IAnalysisExecutor
from tools.revisor_geral import OpenAILLMExecutor

class AnalysisExecutorFactory:
    """
    Factory para instanciar executores de análise conforme configuração.
    """
    @staticmethod
    def create(executor_type: str, **kwargs) -> IAnalysisExecutor:
        if executor_type == 'openai':
            return OpenAILLMExecutor(kwargs['openai_api_key'], kwargs['prompt_dir'])
        raise ValueError(f"Tipo de executor de análise '{executor_type}' não suportado.")
