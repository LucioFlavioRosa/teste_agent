from tools import revisor_geral

class RevisorGeralAdapter:
    """
    Adapter para execução de análise LLM, desacoplando dependência OpenAI.
    """
    def executar_analise_llm(self, tipo_analise, codigo, analise_extra, model_name, max_token_out):
        return revisor_geral.executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=codigo,
            analise_extra=analise_extra,
            model_name=model_name,
            max_token_out=max_token_out
        )
