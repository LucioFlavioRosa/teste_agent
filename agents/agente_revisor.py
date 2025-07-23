from typing import Optional, Dict, Any
from tools import github_reader
from tools.revisor_geral import executar_analise_llm

MODELO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000

ANALISES_VALIDAS = ["design", "pentest", "seguranca", "terraform"]

def validar_parametros(tipo_analise: str, repositorio: Optional[str], codigo: Optional[str]) -> None:
    """Valida os parâmetros obrigatórios para execução da análise."""
    if tipo_analise not in ANALISES_VALIDAS:
        raise ValueError(
            f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {ANALISES_VALIDAS}")
    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")

def carregar_codigo_do_repositorio(repositorio: str, tipo_analise: str) -> Dict[str, Any]:
    """Carrega o código do repositório do GitHub para análise."""
    try:
        print(f'Iniciando a leitura do repositório: {repositorio}')
        codigo_para_analise = github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo_para_analise
    except Exception as e:
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e

def obter_codigo_para_analise(tipo_analise: str, repositorio: Optional[str], codigo: Optional[str]) -> Dict[str, Any]:
    """Obtém o código a ser analisado, seja do repositório ou fornecido diretamente."""
    validar_parametros(tipo_analise, repositorio, codigo)
    if codigo is not None:
        return codigo
    return carregar_codigo_do_repositorio(repositorio=repositorio, tipo_analise=tipo_analise)

def executar_analise(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[str] = None,
    instrucoes_extras: str = "",
    model_name: str = MODELO_LLM,
    max_token_out: int = MAX_TOKENS_SAIDA
) -> Dict[str, Any]:
    """
    Orquestra o processo de análise de código, validando parâmetros, carregando o código
    e executando a análise LLM.
    """
    codigo_para_analise = obter_codigo_para_analise(tipo_analise, repositorio, codigo)
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
