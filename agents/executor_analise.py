from agents.contexto import AnaliseContexto
from tools.revisor_geral import executar_analise_llm

class ExecutorAnalise:
    """
    Responsável por executar a análise usando o LLM, desacoplando a integração externa.
    """
    def executar(self, contexto: AnaliseContexto, codigo_para_analise):
        return executar_analise_llm(
            tipo_analise=contexto.tipo_analise,
            codigo=str(codigo_para_analise),
            analise_extra=contexto.instrucoes_extras,
            model_name=contexto.model_name,
            max_token_out=contexto.max_token_out
        )
