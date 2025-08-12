from typing import Optional, Dict, Any, Callable
from tools import github_reader
from tools.revisor_geral import executar_analise_llm

MODELO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000
ANALISES_VALIDAS = [
    "design", "pentest", "seguranca", "terraform"
]

def validar_tipo_analise(tipo_analise: str) -> None:
    """Valida se o tipo de análise está entre os permitidos."""
    if tipo_analise not in ANALISES_VALIDAS:
        raise ValueError(
            f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {ANALISES_VALIDAS}"
        )

def obter_codigo(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[str] = None,
    leitor_codigo: Callable = github_reader.main
) -> Any:
    """Obtém o código para análise a partir de um repositório ou texto fornecido."""
    if repositorio is None and codigo is None:
        raise ValueError(
            "Erro: É obrigatório fornecer 'repositorio' ou 'codigo'."
        )
    if codigo is None:
        print(f'Iniciando a leitura do repositório: {repositorio}')
        return leitor_codigo(repo=repositorio, tipo_de_analise=tipo_analise)
    return codigo

def orquestrar_analise(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[str] = None,
    instrucoes_extras: str = "",
    model_name: str = MODELO_LLM,
    max_token_out: int = MAX_TOKENS_SAIDA,
    executor_llm: Callable = executar_analise_llm,
    leitor_codigo: Callable = github_reader.main
) -> Dict[str, Any]:
    """Orquestra o fluxo de validação e execução da análise."""
    validar_tipo_analise(tipo_analise)
    codigo_para_analise = obter_codigo(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo=codigo,
        leitor_codigo=leitor_codigo
    )
    if not codigo_para_analise:
        return {
            "tipo_analise": tipo_analise,
            "resultado": 'Não foi fornecido nenhum código para análise'
        }
    resultado = executor_llm(
        tipo_analise=tipo_analise,
        codigo=str(codigo_para_analise),
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}

# Alias para compatibilidade retroativa
main = orquestrar_analise
executar_analise = orquestrar_analise
