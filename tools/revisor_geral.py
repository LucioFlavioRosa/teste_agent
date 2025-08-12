import os
from openai import OpenAI
from typing import Dict
from google.colab import userdata

def obter_openai_api_key(userdata_mod=userdata):
    """
    Obtém a chave da API da OpenAI de forma desacoplada.
    """
    return userdata_mod.get('OPENAI_API_KEY')

def criar_openai_client(api_key: str, openai_mod=OpenAI):
    """
    Cria uma instância do cliente OpenAI.
    """
    return openai_mod(api_key=api_key)

def carregar_prompt(tipo_analise: str, base_dir=None) -> str:
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

def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int,
    openai_client=None,
    carregar_prompt_func=carregar_prompt
) -> str:
    """
    Executa a análise usando LLM da OpenAI.
    """
    prompt_sistema = carregar_prompt_func(tipo_analise)
    mensagens = [
        {"role": "system", "content": prompt_sistema},
        {'role': 'user', 'content': codigo},
        {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
    ]
    try:
        if openai_client is None:
            api_key = obter_openai_api_key()
            if not api_key:
                raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")
            openai_client = criar_openai_client(api_key)
        response = openai_client.chat.completions.create(
            model=model_name,
            messages=mensagens,
            temperature=0.5,
            max_tokens=max_token_out
        )
        conteudo_resposta = response.choices[0].message.content.strip()
        return conteudo_resposta
    except Exception as e:
        # Logging pode ser adicionado aqui
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {e}") from e
