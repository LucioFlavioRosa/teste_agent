from openai import OpenAI
from typing import List, Dict
from tools.interfaces.llm_client_interface import LLMClientInterface
from tools.interfaces.credentials_provider_interface import CredentialsProviderInterface

class OpenAIClient(LLMClientInterface):
    def __init__(self, credentials_provider: CredentialsProviderInterface):
        api_key = credentials_provider.get_openai_api_key()
        if not api_key:
            raise ValueError("A chave da API da OpenAI não foi encontrada.")
        self.client = OpenAI(api_key=api_key)
    
    def chat_completion(self, messages: List[Dict[str, str]], model_name: str, max_tokens: int) -> str:
        response = self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.5,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()