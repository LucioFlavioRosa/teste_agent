from tools.revisor_geral import executar_analise_llm

class AnalysisRegistry:
    """
    Registry de estratégias de análise para facilitar extensão e desacoplamento.
    """
    _strategies = {}

    @classmethod
    def register(cls, tipo_analise, strategy_func):
        cls._strategies[tipo_analise] = strategy_func

    @classmethod
    def get_strategy(cls, tipo_analise):
        if tipo_analise not in cls._strategies:
            raise ValueError(f"Tipo de análise '{tipo_analise}' não registrado.")
        return cls._strategies[tipo_analise]

    @classmethod
    def is_valid(cls, tipo_analise):
        return tipo_analise in cls._strategies

    @classmethod
    def list_types(cls):
        return list(cls._strategies.keys())

# Registro padrão das estratégias existentes
for tipo in ["design", "pentest", "seguranca", "terraform"]:
    AnalysisRegistry.register(
        tipo,
        lambda codigo, analise_extra, model_name, max_token_out, openai_client=None, tipo_analise=tipo: executar_analise_llm(
            codigo=codigo,
            analise_extra=analise_extra,
            model_name=model_name,
            max_token_out=max_token_out,
            tipo_analise=tipo_analise,
            openai_client=openai_client
        )
    )
