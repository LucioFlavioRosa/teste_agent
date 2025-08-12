from typing import Optional, Dict, Any
from tools import github_reader
from tools.revisor_geral import executar_analise_llm

MODELO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000

ANALISES_VALIDAS = ["design", "pentest", "seguranca", "terraform"]

def obter_codigo_para_analise(repositorio: Optional[str], tipo_analise: str, codigo: Optional[str]) -> str:
    """
    Obtém o código-fonte a ser analisado, seja do repositório ou código fornecido diretamente.
    """
    if repositorio:
        print(f'Iniciando a leitura do repositório: {repositorio}')
        return github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)
    elif codigo:
        return codigo
    else:
        raise ValueError("É obrigatório fornecer 'repositorio' ou 'codigo'.")

def validar_tipo_analise(tipo_analise: str) -> None:
    """
    Valida se o tipo de análise está entre os permitidos.
    """
    if tipo_analise not in ANALISES_VALIDAS:
        raise ValueError(
            f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {ANALISES_VALIDAS}")

def preparar_parametros(tipo_analise: str,
                       repositorio: Optional[str] = None,
                       codigo: Optional[str] = None,
                       instrucoes_extras: str = "",
                       model_name: str = MODELO_LLM,
                       max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    """
    Prepara e valida todos os parâmetros necessários para a análise.
    """
    validar_tipo_analise(tipo_analise)
    codigo_para_analise = obter_codigo_para_analise(repositorio, tipo_analise, codigo)
    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
    return {
        "tipo_analise": tipo_analise,
        "codigo_para_analise": codigo_para_analise,
        "instrucoes_extras": instrucoes_extras,
        "model_name": model_name,
        "max_token_out": max_token_out
    }

def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo: Optional[str] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    """
    Orquestra o fluxo de análise, separando validação, preparação e execução da análise LLM.
    """
    parametros = preparar_parametros(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo=codigo,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
    if "resultado" in parametros:
        return parametros
    resultado = executar_analise_llm(
        tipo_analise=tipo_analise,
        codigo=str(parametros["codigo_para_analise"]),
        analise_extra=parametros["instrucoes_extras"],
        model_name=parametros["model_name"],
        max_token_out=parametros["max_token_out"]
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}
