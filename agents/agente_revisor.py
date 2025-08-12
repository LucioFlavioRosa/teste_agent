from typing import Optional, Dict, Any
from tools import github_reader
from tools.revisor_geral import executar_analise_llm
from tools.validator import AnaliseValidator
from tools.llm_client import LLMClient


MODELO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000


def code_from_repo(repositorio: str, tipo_analise: str) -> Dict[str, str]:
    """Obtém o código do repositório para análise."""
    print(f'Iniciando a leitura do repositório: {repositorio}')
    try:
        codigo_para_analise = github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo_para_analise
    except Exception as e:
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e


def validation(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None) -> Dict[str, str]:
    """Valida os parâmetros de entrada para a análise."""
    AnaliseValidator.validar_tipo_analise(tipo_analise)
    AnaliseValidator.validar_origem_codigo(repositorio, codigo)
    if codigo is None:
        return code_from_repo(tipo_analise=tipo_analise, repositorio=repositorio)
    else:
        return codigo


def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo: Optional[str] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    """
    Orquestra o processo de análise: valida entradas, obtém código e executa a análise LLM.
    """
    codigo_para_analise = validation(tipo_analise=tipo_analise,
                                     repositorio=repositorio,
                                     codigo=codigo)
    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
    else:
        llm_client = LLMClient()
        resultado = llm_client.executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=str(codigo_para_analise),
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        return {"tipo_analise": tipo_analise, "resultado": resultado}
