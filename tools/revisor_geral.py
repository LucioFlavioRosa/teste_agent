import os
from openai import OpenAI
from typing import Dict
from google.colab import userdata

def obter_openai_client(api_key: str = None):
    """
    Permite injeção de dependência para o cliente OpenAI (facilita testes/mocks).
    """
    if not api_key:
        api_key = userdata.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")
    return OpenAI(api_key=api_key)

def carregar_prompt(tipo_analise: str) -> str:
    """
    Carrega o conteúdo do arquivo de prompt correspondente.
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
    max_token_out: int,
    openai_client=None
) -> str:
    """
    Executa a análise usando o LLM, permitindo injeção do cliente para testes.
    """
    if openai_client is None:
        openai_client = obter_openai_client()
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
