from typing import Optional, Dict, Any, Callable
from tools import github_reader
from tools.revisor_geral import executar_analise_llm
from enum import Enum


class TipoAnalise(Enum):
    DESIGN = "design"
    PENTEST = "pentest"
    SEGURANCA = "seguranca"
    TERRAFORM = "terraform"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_


def obter_codigo_do_repositorio(repositorio: str, tipo_analise: str) -> Dict[str, str]:
    """
    Obtém o código do repositório remoto usando a ferramenta github_reader.
    """
    try:
        print(f'Iniciando a leitura do repositório: {repositorio}')
        codigo_para_analise = github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo_para_analise
    except Exception as e:
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e


def validar_parametros(tipo_analise: str,
                      repositorio: Optional[str] = None,
                      codigo: Optional[str] = None) -> None:
    """
    Valida os parâmetros de entrada para a análise de código.
    """
    if not TipoAnalise.has_value(tipo_analise):
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {[v.value for v in TipoAnalise]}")
    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")


def preparar_codigo_para_analise(tipo_analise: str,
                                 repositorio: Optional[str] = None,
                                 codigo: Optional[str] = None) -> str:
    """
    Obtém o código a ser analisado, seja do repositório ou diretamente da entrada.
    """
    if codigo is None:
        return obter_codigo_do_repositorio(repositorio=repositorio, tipo_analise=tipo_analise)
    return codigo


def executar_analise(tipo_analise: str,
                    repositorio: Optional[str] = None,
                    codigo: Optional[str] = None,
                    instrucoes_extras: str = "",
                    model_name: str = 'gpt-4.1',
                    max_token_out: int = 3000,
                    executor_llm: Callable = executar_analise_llm) -> Dict[str, Any]:
    """
    Orquestra a execução da análise, separando a lógica de validação, obtenção de código e delegação para LLM.
    """
    validar_parametros(tipo_analise, repositorio, codigo)
    codigo_para_analise = preparar_codigo_para_analise(tipo_analise, repositorio, codigo)
    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
    resultado = executor_llm(
        tipo_analise=tipo_analise,
        codigo=str(codigo_para_analise),
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}
