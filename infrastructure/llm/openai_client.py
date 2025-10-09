from openai import OpenAI
from google.colab import userdata
from infrastructure.llm.llm_client_interface import ILLMClient

class OpenAIClient(ILLMClient):
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = userdata.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError('A chave da API da OpenAI não foi encontrada.')
        self._client = OpenAI(api_key=api_key)

    def chat_completion(self, messages, model, temperature, max_tokens):
        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f'Erro na comunicação com OpenAI: {type(e).__name__}: {e}')

    def validate_connection(self):
        try:
            self._client.models.list()
            return True
        except Exception:
            return False
