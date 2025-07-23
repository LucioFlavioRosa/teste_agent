import os
from openai import OpenAI
from typing import Dict, Callable
from google.colab import userdata


def obter_openai_client(api_key: str = None) -> OpenAI:
    """
    Permite injeção do client OpenAI para facilitar testes.
    """
    if api_key is None:
        api_key = userdata.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")
    return OpenAI(api_key=api_key)


def carregar_prompt(tipo_analise: str, base_dir: str = None) -> str:
    """
    Carrega o conteúdo do arquivo de prompt correspondente.
    """
    if base_dir is None:
        base_dir = os.path.dirname(__file__)
    caminho_prompt = os.path.join(base_dir, 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")


def montar_mensagens_para_llm(prompt_sistema: str, codigo: str, analise_extra: str) -> list:
    """
    Separa a montagem das mensagens para o LLM.
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
    max_token_out: int,
    openai_client_factory: Callable = obter_openai_client,
    carregar_prompt_func: Callable = carregar_prompt
) -> str:
    """
    Executa a análise usando o LLM, separando montagem de prompt e tratamento de exceções.
    """
    prompt_sistema = carregar_prompt_func(tipo_analise)
    mensagens = montar_mensagens_para_llm(prompt_sistema, codigo, analise_extra)
    try:
        openai_client = openai_client_factory()
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
