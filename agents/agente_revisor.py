from typing import Optional, Dict, Any

from tools import github_reader
from tools.revisor_geral import executar_analise_llm

MODELO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000

ANALISES_VALIDAS = ["design", "pentest", "seguranca", "terraform"]

def code_from_repo(repositorio: str, tipo_analise: str):
    """
    Lê o código do repositório do GitHub para análise.
    """
    try:
        print('Iniciando a leitura do repositório: ' + repositorio)
        codigo_para_analise = github_reader.main(
            repo=repositorio,
            tipo_de_analise=tipo_analise
        )
        return codigo_para_analise
    except Exception as e:
        raise RuntimeError(
            f"Falha ao executar a análise de '{tipo_analise}': {e}") from e

def validar_parametros(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None):
    """
    Valida os parâmetros obrigatórios para a análise.
    """
    if tipo_analise not in ANALISES_VALIDAS:
        raise ValueError(
            f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {ANALISES_VALIDAS}")
    if repositorio is None and codigo is None:
        raise ValueError(
            "Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")

def preparar_codigo_para_analise(tipo_analise: str, repositorio: Optional[str], codigo: Optional[str]):
    """
    Prepara o código a ser analisado, lendo do repositório se necessário.
    """
    if codigo is None:
        return code_from_repo(
            tipo_analise=tipo_analise,
            repositorio=repositorio
        )
    return codigo

def main(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[str] = None,
    instrucoes_extras: str = "",
    model_name: str = MODELO_LLM,
    max_token_out: int = MAX_TOKENS_SAIDA
) -> Dict[str, Any]:
    """
    Orquestra a análise do código fonte via LLM, após validação e preparação dos parâmetros.
    """
    validar_parametros(tipo_analise, repositorio, codigo)
    codigo_para_analise = preparar_codigo_para_analise(tipo_analise, repositorio, codigo)
    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
    resultado = executar_analise_llm(
        tipo_analise=tipo_analise,
        codigo=str(codigo_para_analise),
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}
