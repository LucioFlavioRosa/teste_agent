from domain/interfaces/llm_interface import ILLMProvider
from openai import OpenAI
from google.colab import userdata

class OpenAILLMProvider(ILLMProvider):
    def __init__(self):
        OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')
        if not OPENAI_API_KEY:
            raise ValueError("A chave da API da OpenAI não foi encontrada.")
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)

    def executar_analise(self, prompt_sistema, mensagens, model_name, max_tokens):
        response = self.openai_client.chat.completions.create(
            model=model_name,
            messages=mensagens,
            temperature=0.5,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()