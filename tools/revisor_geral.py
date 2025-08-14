"""
Executa análise de código-fonte via LLM (OpenAI) usando prompts especializados.

Este módulo carrega prompts específicos para cada tipo de análise e executa chamadas à API da OpenAI.
Requer configuração prévia de chave de API via `google.colab.userdata`.
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
        tipo_analise (str): Tipo da análise (ex: 'pentest', 'design').

    Returns:
        str: Conteúdo do prompt Markdown.

    Raises:
        ValueError: Se o arquivo de prompt não for encontrado.

    Example:
        >>> carregar_prompt('pentest')
        '# Prompt para análise de pentest...'
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
    Executa análise de código-fonte via modelo de linguagem (LLM).

    Args:
        tipo_analise (str): Tipo da análise (ex: 'pentest', 'design').
        codigo (str): Código-fonte a ser analisado.
        analise_extra (str): Instruções adicionais do usuário.
        model_name (str): Nome do modelo LLM a ser utilizado.
        max_token_out (int): Limite de tokens para a resposta.

    Returns:
        str: Resposta da análise gerada pelo LLM.

    Raises:
        RuntimeError: Se houver falha na chamada à API da OpenAI.

    Example:
        >>> executar_analise_llm('pentest', 'print(1)', '', 'gpt-4', 2000)
        'Nenhuma vulnerabilidade encontrada.'
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
