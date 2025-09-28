import os
from typing import Dict
from tools.interfaces.llm_client_interface import LLMClientInterface
from tools.interfaces.credentials_provider_interface import CredentialsProviderInterface
from tools.implementations.openai_client import OpenAIClient
from tools.implementations.colab_credentials_provider import ColabCredentialsProvider

class RevisorGeral:
    def __init__(self, llm_client: LLMClientInterface = None, credentials_provider: CredentialsProviderInterface = None):
        self.credentials_provider = credentials_provider or ColabCredentialsProvider()
        self.llm_client = llm_client or OpenAIClient(self.credentials_provider)
    
    def carregar_prompt(self, tipo_analise: str) -> str:
        caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
        try:
            with open(caminho_prompt, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError as e:
            raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}") from e
    
    def executar_analise_llm(self, tipo_analise: str, codigo: str, analise_extra: str, model_name: str, max_token_out: int) -> str:
        prompt_sistema = self.carregar_prompt(tipo_analise)
        mensagens = [
            {"role": "system", "content": prompt_sistema},
            {'role': 'user', 'content': codigo},
            {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
        ]
        try:
            return self.llm_client.chat_completion(mensagens, model_name, max_token_out)
        except Exception as e:
            print(f"ERRO: Falha na chamada à API da OpenAI para análise '{tipo_analise}'. Causa: {type(e).__name__}: {e}")
            raise RuntimeError(f"Erro ao comunicar com a OpenAI: {type(e).__name__}: {e}") from e

_revisor_geral_instance = RevisorGeral()

def executar_analise_llm(tipo_analise: str, codigo: str, analise_extra: str, model_name: str, max_token_out: int) -> str:
    return _revisor_geral_instance.executar_analise_llm(tipo_analise, codigo, analise_extra, model_name, max_token_out)