from typing import Optional, Dict, Any
from tools import github_reader
from tools.revisor_geral import executar_analise_llm

modelo_llm = 'gpt-4.1'
max_tokens_saida = 3000

analises_validas = ["design", "pentest", "seguranca", "terraform"]

def code_from_repo(repositorio: str, tipo_analise: str) -> Dict[str, str]:
    """
    Lê o código do repositório GitHub de acordo com o tipo de análise.

    Args:
        repositorio (str): Nome do repositório no formato 'usuario/repositorio'.
        tipo_analise (str): Tipo de análise desejada (ex: 'design', 'pentest').

    Returns:
        Dict[str, str]: Dicionário de arquivos e seus respectivos conteúdos.
    """
    try:
        print('Iniciando a leitura do repositório: ' + repositorio)
        codigo_para_analise = github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo_para_analise
    except Exception as e:
        raise RuntimeError(
            f"Falha ao executar a análise de '{tipo_analise}': {e}") from e

def validation(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None) -> Dict[str, str]:
    """
    Valida os parâmetros de entrada e obtém o código para análise.

    Args:
        tipo_analise (str): Tipo de análise a ser realizada.
        repositorio (Optional[str]): Repositório GitHub a ser analisado.
        codigo (Optional[str]): Código-fonte fornecido diretamente.

    Returns:
        Dict[str, str]: Código a ser analisado.
    """
    if tipo_analise not in analises_validas:
        raise ValueError(
            f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {analises_validas}")
    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")
    if codigo is None:
        codigo_para_analise = code_from_repo(tipo_analise=tipo_analise, repositorio=repositorio)
    else:
        codigo_para_analise = codigo
    return codigo_para_analise

def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo: Optional[str] = None,
                     instrucoes_extras: str = "",
                     model_name: str = modelo_llm,
                     max_token_out: int = max_tokens_saida) -> Dict[str, Any]:
    """
    Orquestra o fluxo de análise, validando parâmetros, obtendo código e executando a análise via LLM.

    Args:
        tipo_analise (str): Tipo de análise ('design', 'pentest', etc).
        repositorio (Optional[str]): Nome do repositório GitHub.
        codigo (Optional[str]): Código-fonte direto.
        instrucoes_extras (str): Instruções adicionais para análise.
        model_name (str): Nome do modelo LLM.
        max_token_out (int): Limite de tokens para resposta.

    Returns:
        Dict[str, Any]: Resultado da análise.
    """
    codigo_para_analise = validation(tipo_analise=tipo_analise,
                                     repositorio=repositorio,
                                     codigo=codigo)
    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
    else:
        resultado = executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=str(codigo_para_analise),
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        return {"tipo_analise": tipo_analise, "resultado": resultado}
