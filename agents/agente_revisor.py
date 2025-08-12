from typing import Optional, Dict, Any
from tools.integracao_github import GithubCodeProvider
from tools.integracao_llm import LLMAnalyzer


ANALISES_VALIDAS = ("design", "pentest", "seguranca", "terraform")


def code_from_repo(repositorio: str, tipo_analise: str) -> Dict[str, Any]:
    """
    Lê o código do repositório GitHub usando o provider abstraído.
    """
    print(f'Iniciando a leitura do repositório: {repositorio}')
    github_provider = GithubCodeProvider()
    return github_provider.get_code(repo=repositorio, tipo_de_analise=tipo_analise)


def validate_analise(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None) -> Any:
    """
    Valida os parâmetros de entrada para análise.
    """
    if tipo_analise not in ANALISES_VALIDAS:
        raise ValueError(
            f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {ANALISES_VALIDAS}")

    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")

    if codigo is None:
        codigo_para_analise = code_from_repo(
            tipo_analise=tipo_analise, repositorio=repositorio)
    else:
        codigo_para_analise = codigo
    return codigo_para_analise


def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo: Optional[str] = None,
                     instrucoes_extras: str = "",
                     model_name: str = 'gpt-4.1',
                     max_token_out: int = 3000) -> Dict[str, Any]:
    """
    Orquestra o fluxo de análise utilizando validação e integração LLM abstraída.
    """
    codigo_para_analise = validate_analise(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo=codigo)

    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}

    llm_analyzer = LLMAnalyzer()
    resultado = llm_analyzer.executar_analise_llm(
        tipo_analise=tipo_analise,
        codigo=str(codigo_para_analise),
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}
