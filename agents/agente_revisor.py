from typing import Optional, Dict, Any
from tools.github_reader_adapter import GithubRepoReader
from tools.revisor_geral_adapter import RevisorGeralAdapter


MODELO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000

ANALISES_VALIDAS = ["design", "pentest", "seguranca", "terraform"]

def code_from_repo(repositorio: str, tipo_analise: str, github_reader=None):
    """
    Obtém código do repositório usando um leitor de repositório (Adapter).
    """
    if github_reader is None:
        github_reader = GithubRepoReader()
    try:
        print('Iniciando a leitura do repositório: ' + repositorio)
        codigo_para_analise = github_reader.get_code(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo_para_analise
    except Exception as e:
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e

def validation(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None, github_reader=None):
    """
    Valida os parâmetros de entrada para análise.
    """
    if tipo_analise not in ANALISES_VALIDAS:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {ANALISES_VALIDAS}")
    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")
    if codigo is None:
        codigo_para_analise = code_from_repo(tipo_analise=tipo_analise, repositorio=repositorio, github_reader=github_reader)
    else:
        codigo_para_analise = codigo
    return codigo_para_analise

def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo: Optional[str] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA,
                     github_reader=None,
                     revisor_geral=None) -> Dict[str, Any]:
    """
    Orquestra a execução da análise, desacoplada das dependências externas.
    """
    if revisor_geral is None:
        revisor_geral = RevisorGeralAdapter()
    codigo_para_analise = validation(tipo_analise=tipo_analise,
                                     repositorio=repositorio,
                                     codigo=codigo,
                                     github_reader=github_reader)
    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
    resultado = revisor_geral.executar_analise_llm(
        tipo_analise=tipo_analise,
        codigo=str(codigo_para_analise),
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}
