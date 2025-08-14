from typing import Optional, Dict, Any
from interfaces.code_source_interface import ICodeSource
from interfaces.analysis_executor_interface import IAnalysisExecutor


class AnalysisOrchestrator:
    """
    Orquestrador principal para execução de análises.
    Recebe dependências via injeção (fonte de código e executor de análise).
    """
    def __init__(self, code_source: ICodeSource, analysis_executor: IAnalysisExecutor):
        self.code_source = code_source
        self.analysis_executor = analysis_executor
        self.valid_analysis_types = self.analysis_executor.get_supported_analysis_types()

    def validate(self, tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None):
        if tipo_analise not in self.valid_analysis_types:
            raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {self.valid_analysis_types}")
        if repositorio is None and codigo is None:
            raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")

    def obter_codigo_para_analise(self, tipo_analise: str, repositorio: Optional[str], codigo: Optional[str]):
        if codigo is not None:
            return codigo
        return self.code_source.get_code(repo=repositorio, tipo_analise=tipo_analise)

    def executar_analise(self, tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None, instrucoes_extras: str = "", model_name: Optional[str] = None, max_token_out: Optional[int] = None) -> Dict[str, Any]:
        self.validate(tipo_analise, repositorio, codigo)
        codigo_para_analise = self.obter_codigo_para_analise(tipo_analise, repositorio, codigo)
        if not codigo_para_analise:
            return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
        resultado = self.analysis_executor.execute_analysis(
            tipo_analise=tipo_analise,
            codigo=str(codigo_para_analise),
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        return {"tipo_analise": tipo_analise, "resultado": resultado}
