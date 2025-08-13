import os
from openai import OpenAI
from typing import Dict
from tools.secrets_provider import obter_openai_api_key
import logging

logger = logging.getLogger(__name__)

openai_client = OpenAI(api_key=obter_openai_api_key())

def carregar_prompt(tipo_analise: str) -> str:
    """
    Carrega o conteúdo do arquivo de prompt correspondente.
    """
    caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")
        raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")

def montar_mensagens(prompt_sistema: str, codigo: str, analise_extra: str) -> list:
    """
    Monta a lista de mensagens para a chamada da API OpenAI.
    """
    return [
        {"role": "system", "content": prompt_sistema},
        {'role': 'user', 'content': codigo},
        {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
    ]

def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int
) -> str:
    """
    Executa a análise LLM, separando carregamento de prompt, montagem de mensagens e chamada da API.
    """
    prompt_sistema = carregar_prompt(tipo_analise)
    mensagens = montar_mensagens(prompt_sistema, codigo, analise_extra)
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
        logger.error(f"Falha na chamada à API da OpenAI para análise '{tipo_analise}': {e}")
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {e}") from e
