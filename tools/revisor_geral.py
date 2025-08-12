import os
from typing import Dict


def carregar_prompt(tipo_analise: str) -> str:
    """Carrega o conteúdo do arquivo de prompt correspondente."""
    caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")


def executar_analise_llm(tipo_analise: str,
                         codigo: str,
                         analise_extra: str,
                         model_name: str,
                         max_token_out: int,
                         openai_client=None) -> str:
    """
    Executa a análise via LLM, recebendo o cliente como dependência para facilitar testes.
    """
    prompt_sistema = carregar_prompt(tipo_analise)
    mensagens = [
        {"role": "system", "content": prompt_sistema},
        {'role': 'user', 'content': codigo},
        {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
    ]
    if openai_client is None:
        from tools.llm_client import LLMClient
        openai_client = LLMClient().get_openai_client()
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
