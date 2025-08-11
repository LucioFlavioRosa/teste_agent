import os
from openai import OpenAI
from typing import Dict
from google.colab import userdata

class PromptLoader:
    """
    Responsável por carregar prompts de análise.
    """
    def __init__(self, prompt_dir=None):
        self.prompt_dir = prompt_dir or os.path.join(os.path.dirname(__file__), 'prompts')

    def carregar_prompt(self, tipo_analise: str) -> str:
        caminho_prompt = os.path.join(self.prompt_dir, f'{tipo_analise}.md')
        try:
            with open(caminho_prompt, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")

class LLMClient:
    """
    Wrapper para o cliente OpenAI, facilitando injeção/mocking.
    """
    def __init__(self, api_key=None):
        api_key = api_key or userdata.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")
        self.client = OpenAI(api_key=api_key)

    def chat_completion(self, model, messages, temperature, max_tokens):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()

def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int,
    prompt_loader: PromptLoader = None,
    llm_client: LLMClient = None
) -> str:
    prompt_loader = prompt_loader or PromptLoader()
    llm_client = llm_client or LLMClient()
    prompt_sistema = prompt_loader.carregar_prompt(tipo_analise)
    mensagens = [
        {"role": "system", "content": prompt_sistema},
        {'role': 'user', 'content': codigo},
        {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
    ]
    try:
        return llm_client.chat_completion(
            model=model_name,
            messages=mensagens,
            temperature=0.5,
            max_tokens=max_token_out
        )
    except Exception as e:
        print(f"ERRO: Falha na chamada à API da OpenAI para análise '{tipo_analise}'. Causa: {e}")
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {e}") from e
