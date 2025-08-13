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
        tipo_analise (str): Tipo de análise (ex: 'design', 'pentest').

    Returns:
        str: Conteúdo do arquivo de prompt.

    Raises:
        ValueError: Se o arquivo de prompt não for encontrado.
    """
    caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompt', f'{tipo_analise}.md')
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
    Executa a análise LLM utilizando o prompt e parâmetros fornecidos.

    Args:
        tipo_analise (str): Tipo de análise a ser realizada.
        codigo (str): Código-fonte a ser analisado.
        analise_extra (str): Instruções extras do usuário.
        model_name (str): Nome do modelo LLM a ser utilizado.
        max_token_out (int): Máximo de tokens de saída.

    Returns:
        str: Conteúdo da resposta da análise.

    Raises:
        RuntimeError: Se houver falha na comunicação com a OpenAI.
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
