from typing import Optional, Dict, Any
from agents.validation import ValidationService
from agents.analysis_factory import AnalysisFactory


def main(tipo_analise: str,
         repositorio: Optional[str] = None,
         codigo: Optional[str] = None,
         instrucoes_extras: str = "",
         model_name: str = None,
         max_token_out: int = None) -> Dict[str, Any]:
    """
    Função principal de orquestração para análise de código.
    Desacoplada de validação e execução de análise.
    """
    validation_service = ValidationService()
    codigo_para_analise = validation_service.validate(tipo_analise=tipo_analise,
                                                      repositorio=repositorio,
                                                      codigo=codigo)
    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}

    analysis_strategy = AnalysisFactory.get_strategy(tipo_analise)
    resultado = analysis_strategy.execute(
        tipo_analise=tipo_analise,
        codigo=str(codigo_para_analise),
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}
