import os
import logging

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)

class OpenAIClientAdapter:
    """
    Adaptador para integração com OpenAI, permite injeção para testes.
    """
    def __init__(self, api_key=None):
        if OpenAI is None:
            raise ImportError("openai package não encontrado.")
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            try:
                from google.colab import userdata
                self.api_key = userdata.get('OPENAI_API_KEY')
            except ImportError:
                pass
        if not self.api_key:
            raise ValueError("A chave da API da OpenAI não foi encontrada. Defina OPENAI_API_KEY.")
        self.client = OpenAI(api_key=self.api_key)

    def chat_completion(self, model, messages, temperature, max_tokens):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
