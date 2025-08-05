from typing import Optional, Dict, Any
from services.analysis_service import AnalysisService, AnalysisConfig
from services.validation_service import ValidationService


def main(tipo_analise: str,
         repositorio: Optional[str] = None,
         codigo: Optional[str] = None,
         instrucoes_extras: str = "",
         model_name: Optional[str] = None,
         max_token_out: Optional[int] = None) -> Dict[str, Any]:
    """
    Orquestra a execução da análise, delegando responsabilidades a serviços especializados.
    """
    # Configuração padrão
    analysis_config = AnalysisConfig(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo=codigo,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )

    # Validação das entradas
    validator = ValidationService()
    try:
        validator.validate_analysis_type(analysis_config.tipo_analise)
        validator.validate_input_sources(analysis_config.repositorio, analysis_config.codigo)
    except ValueError as err:
        return {"tipo_analise": tipo_analise, "resultado": str(err)}

    # Serviço de análise
    analysis_service = AnalysisService()
    try:
        resultado = analysis_service.run_analysis(analysis_config)
        return {"tipo_analise": tipo_analise, "resultado": resultado}
    except Exception as e:
        return {"tipo_analise": tipo_analise, "resultado": f"Erro interno: {e}"}
