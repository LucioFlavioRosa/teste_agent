from typing import Optional, Dict, Any
from tools.adapters.github_adapter import GithubRepoReader
from tools.adapters.openai_adapter import OpenAIClientAdapter
from tools.analysis_registry import AnalysisRegistry
import logging

logger = logging.getLogger(__name__)

class AnalysisContext:
    """
    Encapsula os parâmetros recorrentes para análise.
    """
    def __init__(self, tipo_analise: str, repositorio: Optional[str] = None,
                 codigo: Optional[str] = None, instrucoes_extras: str = "",
                 model_name: str = 'gpt-4.1', max_token_out: int = 3000):
        self.tipo_analise = tipo_analise
        self.repositorio = repositorio
        self.codigo = codigo
        self.instrucoes_extras = instrucoes_extras
        self.model_name = model_name
        self.max_token_out = max_token_out


def validar_tipo_analise(tipo_analise: str):
    if not AnalysisRegistry.is_valid(tipo_analise):
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {AnalysisRegistry.list_types()}")


def obter_codigo_para_analise(ctx: AnalysisContext, github_reader=None):
    if ctx.codigo is not None:
        return ctx.codigo
    if ctx.repositorio is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")
    github_reader = github_reader or GithubRepoReader()
    logger.info(f'Iniciando a leitura do repositório: {ctx.repositorio}')
    try:
        return github_reader.read_repo(repo=ctx.repositorio, tipo_de_analise=ctx.tipo_analise)
    except Exception as e:
        logger.error(f"Falha ao executar a análise de '{ctx.tipo_analise}': {e}")
        raise RuntimeError(f"Falha ao executar a análise de '{ctx.tipo_analise}': {e}") from e


def executar_analise(ctx: AnalysisContext, github_reader=None, openai_client=None) -> Dict[str, Any]:
    validar_tipo_analise(ctx.tipo_analise)
    codigo_para_analise = obter_codigo_para_analise(ctx, github_reader=github_reader)
    if not codigo_para_analise:
        return {"tipo_analise": ctx.tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
    analysis_strategy = AnalysisRegistry.get_strategy(ctx.tipo_analise)
    resultado = analysis_strategy(
        codigo=str(codigo_para_analise),
        analise_extra=ctx.instrucoes_extras,
        model_name=ctx.model_name,
        max_token_out=ctx.max_token_out,
        openai_client=openai_client
    )
    return {"tipo_analise": ctx.tipo_analise, "resultado": resultado}


# Interface de compatibilidade para uso legado

def main(tipo_analise: str,
         repositorio: Optional[str] = None,
         codigo: Optional[str] = None,
         instrucoes_extras: str = "",
         model_name: str = 'gpt-4.1',
         max_token_out: int = 3000) -> Dict[str, Any]:
    ctx = AnalysisContext(tipo_analise=tipo_analise,
                         repositorio=repositorio,
                         codigo=codigo,
                         instrucoes_extras=instrucoes_extras,
                         model_name=model_name,
                         max_token_out=max_token_out)
    return executar_analise(ctx)

# Mantém compatibilidade com chamadas antigas
executar_analise = executar_analise

