from typing import Optional

class AnaliseContexto:
    """
    Objeto de contexto para transportar parâmetros de análise.
    """
    def __init__(self, tipo_analise: str, repositorio: Optional[str], codigo: Optional[str], instrucoes_extras: str, model_name: str, max_token_out: int):
        self.tipo_analise = tipo_analise
        self.repositorio = repositorio
        self.codigo = codigo
        self.instrucoes_extras = instrucoes_extras
        self.model_name = model_name
        self.max_token_out = max_token_out
