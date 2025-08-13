import os
from openai import OpenAI
from typing import Dict
from google.colab import userdata

OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

def carregar_prompt(tipo_analise: str, prompt_loader_func=None) -> str:
    """
    Carrega o conteúdo do arquivo de prompt correspondente.
    Args:
        tipo_analise (str): Tipo de análise.
        prompt_loader_func (callable, opcional): Função customizada para carregar prompt.
    Returns:
        str: Conteúdo do prompt.
    """
    if prompt_loader_func is not None:
        return prompt_loader_func(tipo_analise)
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
    prompt_loader_func=None,
    openai_client_instance=None
) -> str:
    """
    Executa a análise LLM, separando montagem do prompt, chamada de API e tratamento de exceção.
    Args:
        tipo_analise (str): Tipo de análise.
        codigo (str): Código a ser analisado.
        analise_extra (str): Instruções extras.
        model_name (str): Nome do modelo.
        max_token_out (int): Máximo de tokens de saída.
        prompt_loader_func (callable, opcional): Função customizada para carregar prompt.
        openai_client_instance (OpenAI, opcional): Instância customizada do cliente OpenAI.
    Returns:
        str: Conteúdo da resposta.
    """
    prompt_sistema = carregar_prompt(tipo_analise, prompt_loader_func=prompt_loader_func)
    mensagens = [
        {"role": "system", "content": prompt_sistema},
        {'role': 'user', 'content': codigo},
        {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
    ]
    client = openai_client_instance if openai_client_instance is not None else openai_client
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=mensagens,
            temperature=0.5,
            max_tokens=max_token_out
        )
        conteudo_resposta = response.choices[0].message.content.strip()
        return conteudo_resposta
    except Exception as exc:
        # Logging pode ser adicionado aqui se necessário
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {exc}") from exc
