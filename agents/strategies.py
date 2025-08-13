from enum import Enum
from typing import Any

class AnalysisType(Enum):
    DESIGN = "design"
    PENTEST = "pentest"
    SEGURANCA = "seguranca"
    TERRAFORM = "terraform"

    @staticmethod
    def from_str(label: str) -> 'AnalysisType':
        label = label.lower()
        for t in AnalysisType:
            if t.value == label:
                return t
        raise ValueError(f"Tipo de análise '{label}' é inválido. Válidos: {[t.value for t in AnalysisType]}")

class AnalysisStrategy:
    def execute(self, codigo: str, analise_extra: str = "") -> Any:
        raise NotImplementedError

class LLMAnalysisStrategy(AnalysisStrategy):
    def __init__(self, llm_client, analysis_type: AnalysisType, model_name: str, max_token_out: int):
        self.llm_client = llm_client
        self.analysis_type = analysis_type
        self.model_name = model_name
        self.max_token_out = max_token_out

    def execute(self, codigo: str, analise_extra: str = "") -> Any:
        return self.llm_client.executar_analise_llm(
            tipo_analise=self.analysis_type.value,
            codigo=codigo,
            analise_extra=analise_extra,
            model_name=self.model_name,
            max_token_out=self.max_token_out
        )

class AnalysisStrategyFactory:
    @staticmethod
    def get_strategy(analysis_type: AnalysisType, llm_client, model_name: str, max_token_out: int) -> AnalysisStrategy:
        # No futuro, pode-se adicionar outras estratégias
        return LLMAnalysisStrategy(llm_client, analysis_type, model_name, max_token_out)
