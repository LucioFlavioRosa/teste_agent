import os
from openai import OpenAI
from typing import Dict, Optional
from google.colab import userdata


class LLMAnalyzer:
    """
    Classe para integração com LLM (OpenAI), permitindo injeção de dependências.
    """
    def __init__(self, openai_api_key: Optional[str] = None, prompts_dir: Optional[str] = None):
        self.api_key = openai_api_key or userdata.get('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")
        self.openai_client = OpenAI(api_key=self.api_key)
        self.prompts_dir = prompts_dir or os.path.join(os.path.dirname(__file__), 'prompts')

    def carregar_prompt(self, tipo_analise: str) -> str:
        caminho_prompt = os.path.join(self.prompts_dir, f'{tipo_analise}.md')
        try:
            with open(caminho_prompt, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")

    def executar_analise_llm(
        self,
        tipo_analise: str,
        codigo: str,
        analise_extra: str,
        model_name: str,
        max_token_out: int
    ) -> str:
        prompt_sistema = self.carregar_prompt(tipo_analise)
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
