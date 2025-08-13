import os
from typing import Dict
from tools.adapters.openai_adapter import OpenAIClientAdapter
import logging

logger = logging.getLogger(__name__)


def carregar_prompt(tipo_analise: str) -> str:
    """Carrega o conteúdo do arquivo de prompt correspondente."""
    caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")


def executar_analise_llm(
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int,
    tipo_analise: str,
    openai_client=None
) -> str:
    prompt_sistema = carregar_prompt(tipo_analise)
    mensagens = [
        {"role": "system", "content": prompt_sistema},
        {'role': 'user', 'content': codigo},
        {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
    ]
    openai_client = openai_client or OpenAIClientAdapter()
    try:
        conteudo_resposta = openai_client.chat_completion(
            model=model_name,
            messages=mensagens,
            temperature=0.5,
            max_tokens=max_token_out
        )
        return conteudo_resposta
    except Exception as e:
        logger.error(f"ERRO: Falha na chamada à API da OpenAI para análise '{tipo_analise}'. Causa: {e}")
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {e}") from e
