import sys
import os

from tools.input_validator import validar_parametros_entrada
from tools.revisor_geral import executar_analise_llm
from tools.github_reader import obter_codigo_repositorio


def orquestrar_analise(tipo_analise, repositorio, caminho_credenciais, extensoes_personalizadas=None):
    """
    Orquestra o fluxo principal de análise: validação, obtenção de código e execução da análise LLM.
    Args:
        tipo_analise (str): Tipo de análise a ser realizada.
        repositorio (str): Endereço do repositório a ser analisado.
        caminho_credenciais (str): Caminho para as credenciais do Github.
        extensoes_personalizadas (list, opcional): Lista de extensões personalizadas.
    Returns:
        dict: Resultado da análise ou mensagem de erro.
    """
    parametros_validos, mensagem = validar_parametros_entrada(tipo_analise, repositorio, caminho_credenciais)
    if not parametros_validos:
        return {"erro": mensagem}

    codigo = obter_codigo_repositorio(repositorio, caminho_credenciais, tipo_analise, extensoes_personalizadas)
    if not codigo:
        return {"erro": "Não foi possível obter o código do repositório."}

    resultado = executar_analise_llm(tipo_analise, repositorio, codigo)
    return resultado


def main():
    """
    Função principal de entrada. Lê argumentos da linha de comando e executa a orquestração.
    """
    if len(sys.argv) < 4:
        print("Uso: python agente_revisor.py <tipo_analise> <repositorio> <caminho_credenciais> [extensoes_personalizadas]")
        sys.exit(1)

    tipo_analise = sys.argv[1]
    repositorio = sys.argv[2]
    caminho_credenciais = sys.argv[3]
    extensoes_personalizadas = sys.argv[4].split(',') if len(sys.argv) > 4 else None

    resultado = orquestrar_analise(tipo_analise, repositorio, caminho_credenciais, extensoes_personalizadas)
    print(resultado)
