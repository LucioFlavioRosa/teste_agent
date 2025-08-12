from typing import Optional, Dict, Any
from tools.github_adapter import GithubAdapter
from tools.revisor_geral import executar_analise_llm
from agents.strategies import ANALISE_STRATEGIES

MODELO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000


def code_from_repo(repositorio: str, tipo_analise: str):
    """
    Recupera o código do repositório usando o adaptador de GitHub.
    """
    print(f'Iniciando a leitura do repositório: {repositorio}')
    github_adapter = GithubAdapter()
    return github_adapter.obter_codigo(repo=repositorio, tipo_de_analise=tipo_analise)


def validation(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None):
    """
    Valida o tipo de análise e a entrada de código ou repositório.
    """
    if tipo_analise not in ANALISE_STRATEGIES:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {list(ANALISE_STRATEGIES.keys())}")

    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")

    if codigo is None:
        codigo_para_analise = code_from_repo(tipo_analise=tipo_analise, repositorio=repositorio)
    else:
        codigo_para_analise = codigo

    return codigo_para_analise


def executar_analise(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[str] = None,
    instrucoes_extras: str = "",
    model_name: str = MODELO_LLM,
    max_token_out: int = MAX_TOKENS_SAIDA
) -> Dict[str, Any]:
    """
    Orquestra a execução da análise, delegando a lógica específica para a estratégia adequada.
    """
    codigo_para_analise = validation(tipo_analise=tipo_analise, repositorio=repositorio, codigo=codigo)

    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}

    strategy = ANALISE_STRATEGIES[tipo_analise]
    resultado = strategy(
        tipo_analise=tipo_analise,
        codigo=codigo_para_analise,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}
