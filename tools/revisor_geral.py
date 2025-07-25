import os
from openai import OpenAI
from typing import Dict
from google.colab import userdata


def carregar_prompt(tipo_analise: str, base_path=None) -> str:
    """
    Carrega o conteúdo do arquivo de prompt correspondente.
    """
    if base_path is None:
        base_path = os.path.dirname(__file__)
    caminho_prompt = os.path.join(base_path, 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")


class AnaliseExecutor:
    """
    Executor desacoplado de análise LLM, permite injeção de cliente e configuração.
    """
    def __init__(self, openai_client=None, prompt_loader=None):
        api_key = userdata.get('OPENAI_API_KEY')
        if not openai_client:
            if not api_key:
                raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")
            self.openai_client = OpenAI(api_key=api_key)
        else:
            self.openai_client = openai_client
        self.prompt_loader = prompt_loader or carregar_prompt

    def executar(self,
                 tipo_analise: str,
                 codigo: str,
                 analise_extra: str,
                 model_name: str,
                 max_token_out: int) -> str:
        prompt_sistema = self.prompt_loader(tipo_analise)
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
