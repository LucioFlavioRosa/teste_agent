from typing import Optional
from tools import github_reader
from tools.revisor_geral import executar_analise_llm


class AnalysisConfig:
    def __init__(self,
                 tipo_analise: str,
                 repositorio: Optional[str] = None,
                 codigo: Optional[str] = None,
                 instrucoes_extras: str = '',
                 model_name: Optional[str] = None,
                 max_token_out: Optional[int] = None):
        self.tipo_analise = tipo_analise
        self.repositorio = repositorio
        self.codigo = codigo
        self.instrucoes_extras = instrucoes_extras
        self.model_name = model_name
        self.max_token_out = max_token_out


class AnalysisService:
    def __init__(self):
        self.default_model = 'gpt-4.1'
        self.default_max_tokens = 3000

    def run_analysis(self, config: AnalysisConfig) -> str:
        codigo_para_analise = self._get_code(config)
        if not codigo_para_analise:
            return 'Não foi fornecido nenhum código para análise'
        resultado = executar_analise_llm(
            tipo_analise=config.tipo_analise,
            codigo=str(codigo_para_analise),
            analise_extra=config.instrucoes_extras,
            model_name=config.model_name or self.default_model,
            max_token_out=config.max_token_out or self.default_max_tokens
        )
        return resultado

    def _get_code(self, config: AnalysisConfig):
        if config.codigo is not None:
            return config.codigo
        if config.repositorio is not None:
            return github_reader.main(repo=config.repositorio, tipo_de_analise=config.tipo_analise)
        return None
