from tools.revisor_geral import executar_analise_llm

class AnaliseExecutor:
    """
    Executor base para diferentes tipos de análise.
    """
    def executar(self, codigo, analise_extra, model_name, max_token_out):
        raise NotImplementedError

class AnaliseLLMExecutor(AnaliseExecutor):
    """
    Executor padrão para análise via LLM.
    """
    def __init__(self, tipo_analise):
        self.tipo_analise = tipo_analise

    def executar(self, codigo, analise_extra, model_name, max_token_out):
        return executar_analise_llm(
            tipo_analise=self.tipo_analise,
            codigo=codigo,
            analise_extra=analise_extra,
            model_name=model_name,
            max_token_out=max_token_out
        )

class AnaliseFactory:
    """
    Factory para instanciar executores de análise conforme o tipo.
    """
    _tipos = ["design", "pentest", "seguranca", "terraform"]

    def tipos_disponiveis(self):
        return self._tipos.copy()

    def criar_executor(self, tipo_analise):
        if tipo_analise in self._tipos:
            return AnaliseLLMExecutor(tipo_analise)
        raise ValueError(f"Tipo de análise '{tipo_analise}' não suportado.")
