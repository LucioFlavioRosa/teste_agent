import os
from openai import OpenAI
from typing import Dict, Protocol
from google.colab import userdata
from abc import ABC, abstractmethod

class ClienteLLM(Protocol):
    def executar_analise(self, mensagens: list, model_name: str, max_token_out: int) -> str:
        pass

class ClienteOpenAI:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def executar_analise(self, mensagens: list, model_name: str, max_token_out: int) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=mensagens,
                temperature=0.5,
                max_tokens=max_token_out
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"ERRO: Falha na chamada à API da OpenAI. Causa: {type(e).__name__}: {e}")
            raise RuntimeError(f"Erro ao comunicar com a OpenAI: {type(e).__name__}: {e}") from e

class CarregadorPrompt:
    @staticmethod
    def carregar(tipo_analise: str) -> str:
        caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
        try:
            with open(caminho_prompt, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError as e:
            raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}") from e

class MontadorMensagens:
    @staticmethod
    def montar(prompt_sistema: str, codigo: str, analise_extra: str) -> list:
        return [
            {"role": "system", "content": prompt_sistema},
            {'role': 'user', 'content': codigo},
            {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
        ]

class ExecutorAnaliseLLM:
    def __init__(self, cliente_llm: ClienteLLM, carregador_prompt: CarregadorPrompt, montador_mensagens: MontadorMensagens):
        self.cliente_llm = cliente_llm
        self.carregador_prompt = carregador_prompt
        self.montador_mensagens = montador_mensagens
    
    def executar(
        self,
        tipo_analise: str,
        codigo: str,
        analise_extra: str,
        model_name: str,
        max_token_out: int
    ) -> str:
        prompt_sistema = self.carregador_prompt.carregar(tipo_analise)
        mensagens = self.montador_mensagens.montar(prompt_sistema, codigo, analise_extra)
        return self.cliente_llm.executar_analise(mensagens, model_name, max_token_out)

def _criar_cliente_padrao() -> ClienteLLM:
    OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")
    return ClienteOpenAI(OPENAI_API_KEY)

_executor_global = ExecutorAnaliseLLM(
    cliente_llm=_criar_cliente_padrao(),
    carregador_prompt=CarregadorPrompt(),
    montador_mensagens=MontadorMensagens()
)

def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int
) -> str:
    return _executor_global.executar(
        tipo_analise=tipo_analise,
        codigo=codigo,
        analise_extra=analise_extra,
        model_name=model_name,
        max_token_out=max_token_out
    )