import os
from openai import OpenAI
from typing import Dict, Protocol
from google.colab import userdata
from abc import ABC, abstractmethod


OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")

class LLMProvider(ABC):
    """Interface abstrata para provedores de LLM."""
    
    @abstractmethod
    def gerar_resposta(self, mensagens: list, model_name: str, temperature: float, max_tokens: int) -> str:
        """Gera uma resposta baseada nas mensagens fornecidas."""
        pass

class OpenAIProvider(LLMProvider):
    """Implementação concreta do provedor OpenAI."""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def gerar_resposta(self, mensagens: list, model_name: str, temperature: float, max_tokens: int) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=mensagens,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"Erro ao comunicar com a OpenAI: {e}") from e

# Instância padrão do provedor
llm_provider = OpenAIProvider(OPENAI_API_KEY)

def carregar_prompt(tipo_analise: str) -> str:
    """Carrega o conteúdo do arquivo de prompt correspondente."""
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
    provider: LLMProvider = None
) -> str:
    
    if provider is None:
        provider = llm_provider
    
    prompt_sistema = carregar_prompt(tipo_analise)

    mensagens = [
        {"role": "system", "content": prompt_sistema},
        {'role': 'user', 'content': codigo},
        {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
    ]

    try:
        conteudo_resposta = provider.gerar_resposta(
            mensagens=mensagens,
            model_name=model_name,
            temperature=0.5,
            max_tokens=max_token_out
        )
        return conteudo_resposta
        
    except Exception as e:
        print(f"ERRO: Falha na chamada à API da OpenAI para análise '{tipo_analise}'. Causa: {e}")
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {e}") from e