from tools.revisor_geral import executar_analise_llm

class AnalysisStrategy:
    """
    Interface para estratégias de análise.
    """
    def execute(self, tipo_analise, codigo, analise_extra, model_name, max_token_out):
        raise NotImplementedError

class LLMAnalysisStrategy(AnalysisStrategy):
    """
    Estratégia padrão para análise usando LLM.
    """
    def execute(self, tipo_analise, codigo, analise_extra, model_name, max_token_out):
        return executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=codigo,
            analise_extra=analise_extra,
            model_name=model_name,
            max_token_out=max_token_out
        )

class AnalysisFactory:
    """
    Factory para selecionar a estratégia de análise.
    """
    @staticmethod
    def get_strategy(tipo_analise):
        # Futuramente pode-se retornar diferentes estratégias
        return LLMAnalysisStrategy()
