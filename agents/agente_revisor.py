import os
import sys

from tools.github_reader import ler_arquivos_do_repositorio
from tools.revisor_geral import executar_analise_llm
from tools.validator import validar_parametros
from tools.external_services import obter_token_github, obter_token_openai


def main(tipo_analise, repositorio):
    """
    Função principal que orquestra a coleta de código,
    validação de parâmetros e execução da análise LLM.

    Args:
        tipo_analise (str): Tipo de análise a ser executada.
        repositorio (str): URL do repositório a ser analisado.

    Returns:
        str: Resultado da análise LLM.
    """
    validar_parametros(tipo_analise, repositorio)
    token_github = obter_token_github()
    token_openai = obter_token_openai()
    codigo = ler_arquivos_do_repositorio(repositorio, tipo_analise, token_github)
    resultado = executar_analise_llm(tipo_analise, codigo, token_openai)
    return resultado
