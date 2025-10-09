from openai import OpenAI
from infrastructure.llm.llm_client_interface import ILLMClient
from typing import List, Dict, Any
from google.colab import userdata

class OpenAIClientAdapter(ILLMClient):
    def __init__(self):
        api_key = userdata.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError('A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.')
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
            raise RuntimeError(f'Erro ao comunicar com a OpenAI: {type(e).__name__}: {e}') from e

    def validate_connection(self) -> bool:
        try:
            # Testa uma chamada simples para validar a conexão
            self.client.models.list()
            return True
        except Exception:
            return False
