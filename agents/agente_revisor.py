from typing import Optional, Dict, Any
from tools import github_reader
from tools.revisor_geral import executar_analise_llm

modelo_llm = 'gpt-4.1'
max_tokens_saida = 3000

analises_validas = ["design", "pentest", "seguranca", "terraform"]

def obter_codigo_do_repositorio(repositorio: str, tipo_analise: str) -> Dict[str, str]:
    """
    Obtém o código do repositório do GitHub para o tipo de análise especificado.

    Args:
        repositorio (str): Nome do repositório GitHub.
        tipo_analise (str): Tipo de análise a ser realizada.

    Returns:
        Dict[str, str]: Dicionário com caminhos de arquivos e seus conteúdos.

    Raises:
        RuntimeError: Se ocorrer erro ao ler o repositório.
    """
    try:
        print(f'Iniciando a leitura do repositório: {repositorio}')
        codigo_para_analise = github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo_para_analise
    except Exception as e:
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e

def validar_parametros(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None) -> Any:
    """
    Valida os parâmetros de entrada para a análise.

    Args:
        tipo_analise (str): Tipo de análise a ser realizada.
        repositorio (Optional[str]): Nome do repositório GitHub.
        codigo (Optional[str]): Código-fonte direto.

    Returns:
        Any: Código a ser analisado.

    Raises:
        ValueError: Se parâmetros obrigatórios estiverem ausentes ou inválidos.
    """
    if tipo_analise not in analises_validas:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {analises_validas}")
    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")
    if codigo is None:
        return obter_codigo_do_repositorio(repositorio=repositorio, tipo_analise=tipo_analise)
    return codigo

def executar_analise(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[str] = None,
    instrucoes_extras: str = "",
    model_name: str = modelo_llm,
    max_token_out: int = max_tokens_saida
) -> Dict[str, Any]:
    """
    Orquestra o fluxo de análise, validando parâmetros e executando a análise LLM.

    Args:
        tipo_analise (str): Tipo de análise a ser realizada.
        repositorio (Optional[str]): Nome do repositório GitHub.
        codigo (Optional[str]): Código-fonte direto.
        instrucoes_extras (str): Instruções adicionais para a análise.
        model_name (str): Nome do modelo LLM a ser usado.
        max_token_out (int): Limite de tokens de saída.

    Returns:
        Dict[str, Any]: Resultado da análise.
    """
    codigo_para_analise = validar_parametros(tipo_analise=tipo_analise, repositorio=repositorio, codigo=codigo)
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
