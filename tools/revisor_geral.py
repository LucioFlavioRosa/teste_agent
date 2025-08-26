import os
import openai
from typing import Dict

def obter_openai_api_key():
    """Obtém a chave da API da OpenAI de diferentes fontes dependendo do ambiente."""
    try:
        # Tenta primeiro o Google Colab
        from google.colab import userdata
        return userdata.get('OPENAI_API_KEY')
    except ImportError:
        # Se não estiver no Colab, tenta variável de ambiente
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("A chave da API da OpenAI não foi encontrada. Configure OPENAI_API_KEY como variável de ambiente ou no Google Colab userdata.")
        return api_key

OPENAI_API_KEY = obter_openai_api_key()
if not OPENAI_API_KEY:
    raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")

# Usar o cliente correto do OpenAI
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

def carregar_prompt(tipo_analise: str) -> str:
    caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError as e:
        raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}") from e

def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int
) -> str:
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
        print(f"ERRO: Falha na chamada à API da OpenAI para análise '{tipo_analise}'. Causa: {type(e).__name__}: {e}")
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {type(e).__name__}: {e}") from e