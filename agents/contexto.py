from typing import Optional

class AnaliseContexto:
    """
    Encapsula os parâmetros recorrentes de análise para evitar data clumps e
    facilitar a passagem de contexto entre camadas.
    """
    def __init__(self, tipo_analise: str, repositorio: Optional[str] = None,
                 codigo: Optional[str] = None, instrucoes_extras: str = "",
                 model_name: Optional[str] = None, max_token_out: Optional[int] = None):
        self.tipo_analise = tipo_analise
        self.repositorio = repositorio
        self.codigo = codigo
        self.instrucoes_extras = instrucoes_extras
        self.model_name = model_name
        self.max_token_out = max_token_out
