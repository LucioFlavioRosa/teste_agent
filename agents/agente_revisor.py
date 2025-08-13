from typing import Optional, Dict, Any
from agents.contexto import AnaliseContexto
from agents.validador import ValidadorDeParametros
from agents.leitor_codigo import LeitorCodigo
from agents.executor_analise import ExecutorAnalise


def executar_analise(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[str] = None,
    instrucoes_extras: str = "",
    model_name: str = None,
    max_token_out: int = None
) -> Dict[str, Any]:
    """
    Orquestra a execução de uma análise de código, separando responsabilidades
    conforme Clean Architecture e SOLID.
    """
    contexto = AnaliseContexto(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo=codigo,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )

    validador = ValidadorDeParametros()
    validador.validar(contexto)

    leitor = LeitorCodigo()
    codigo_para_analise = leitor.obter_codigo(contexto)
    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}

    executor = ExecutorAnalise()
    resultado = executor.executar(contexto, codigo_para_analise)
    return {"tipo_analise": tipo_analise, "resultado": resultado}
