import os
from openai import OpenAI
from typing import Dict
from google.colab import userdata


def _get_openai_api_key():
    return userdata.get('OPENAI_API_KEY')


def _carregar_prompt(tipo_analise: str) -> str:
    """
    Carrega o conteúdo do arquivo de prompt correspondente.
    """
    caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")


class LLMAnalyzer:
    """
    Abstrai a chamada ao LLM (OpenAI), permitindo injeção de cliente e fácil teste/mocks.
    """
    def __init__(self, openai_client=None, api_key=None):
        self.api_key = api_key or _get_openai_api_key()
        if not self.api_key:
            raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")
        self.openai_client = openai_client or OpenAI(api_key=self.api_key)

    def executar_analise_llm(self,
                             tipo_analise: str,
                             codigo: str,
                             analise_extra: str,
                             model_name: str,
                             max_token_out: int) -> str:
        prompt_sistema = _carregar_prompt(tipo_analise)
        mensagens = [
            {"role": "system", "content": prompt_sistema},
            {'role': 'user', 'content': codigo},
            {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
        ]
        try:
            response = self.openai_client.chat.completions.create(
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
