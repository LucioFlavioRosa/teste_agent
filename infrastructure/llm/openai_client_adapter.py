from openai import OpenAI
from infrastructure.llm.llm_client_interface import ILLMClient
from typing import List, Dict, Any
import os
from google.colab import userdata

class OpenAIClientAdapter(ILLMClient):
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = userdata.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError('A chave da API da OpenAI não foi encontrada.')
        self.client = OpenAI(api_key=api_key)

    def chat_completion(self, messages: List[Dict[str, Any]], model: str, temperature: float, max_tokens: int) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f'Erro ao comunicar com a OpenAI: {type(e).__name__}: {e}')

    def validate_connection(self) -> bool:
        try:
            self.client.models.list()
            return True
        except Exception:
            return False
