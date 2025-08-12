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
    Carrega o conteúdo do arquivo de prompt correspondente.
    Args:
        tipo_analise (str): Tipo de análise.
    Returns:
        str: Conteúdo do prompt.
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
    cliente_llm=None,
    prompt_loader=carregar_prompt
) -> str:
    """
    Executa a análise usando LLM (OpenAI).
    Args:
        tipo_analise (str): Tipo de análise.
        codigo (str): Código para análise.
        analise_extra (str): Instruções extras.
        model_name (str): Nome do modelo.
        max_token_out (int): Limite de tokens.
        cliente_llm: Cliente OpenAI (injeção de dependência).
        prompt_loader: Função para carregar prompt.
    Returns:
        str: Conteúdo da resposta do LLM.
    """
    if cliente_llm is None:
        cliente_llm = openai_client
    prompt_sistema = prompt_loader(tipo_analise)
    mensagens = [
        {"role": "system", "content": prompt_sistema},
        {'role': 'user', 'content': codigo},
        {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
    ]
    try:
        response = cliente_llm.chat.completions.create(
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
