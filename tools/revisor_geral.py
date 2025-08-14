"""
Módulo revisor_geral

Orquestra a execução de análises LLM sobre código-fonte, incluindo carregamento de prompts específicos e chamada à API da OpenAI.
"""
import os
from openai import OpenAI
from typing import Dict
from google.colab import userdata

OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

def carregar_prompt(tipo_analise: str) -> str:
    """
    Carrega o conteúdo do arquivo de prompt correspondente ao tipo de análise.

    Args:
        tipo_analise (str): Tipo de análise (ex: 'pentest', 'design').

    Returns:
        str: Conteúdo do prompt em formato texto.

    Raises:
        ValueError: Se o arquivo de prompt não for encontrado.
    """
    caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")

def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int
) -> str:
    """
    Executa a análise do código usando um modelo LLM via API OpenAI.

    Args:
        tipo_analise (str): Tipo de análise (ex: 'pentest', 'design').
        codigo (str): Código-fonte a ser analisado.
        analise_extra (str): Instruções adicionais do usuário.
        model_name (str): Nome do modelo LLM a ser utilizado.
        max_token_out (int): Limite máximo de tokens para a resposta.

    Returns:
        str: Resposta gerada pelo modelo LLM.

    Raises:
        RuntimeError: Se ocorrer erro na comunicação com a API da OpenAI.

    Example:
        >>> executar_analise_llm('pentest', 'print(1)', '', 'gpt-4', 1000)
        'Resultado da análise...'
    """
    prompt_sistema = carregar_prompt(tipo_analise)
    mensagens = [
        {"role": "system", "content": prompt_sistema},
        {'role': 'user', 'content': codigo},
        {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
    ]
    try:
        response = openai_client.chat.completions.create(
            model=model_name,
            messages=mensagens,
            temperature=0.5,
            max_tokens=max_token_out
        )
        conteudo_resposta = response.choices[0].message.content.strip()
        return conteudo_resposta
    except Exception as e:
        print(f"ERRO: Falha na chamada à API da OpenAI para análise '{tipo_analise}'. Causa: {e}")
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {e}") from e
