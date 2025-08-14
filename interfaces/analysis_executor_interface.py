from abc import ABC, abstractmethod

class IAnalysisExecutor(ABC):
    """
    Interface para executores de análise (ex: LLM, análise estática, etc).
    """
    @abstractmethod
    def execute_analysis(self, tipo_analise: str, codigo: str, analise_extra: str, model_name: str = None, max_token_out: int = None) -> str:
        pass

    @abstractmethod
    def get_supported_analysis_types(self):
        pass
