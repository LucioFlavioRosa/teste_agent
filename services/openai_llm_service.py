from openai import OpenAI
from google.colab import userdata
from interfaces.llm_service_interface import ILLMService
from typing import List, Dict

class OpenAILLMService(ILLMService):
    """Implementação do serviço LLM usando OpenAI"""
    
    def __init__(self):
        OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')
        if not OPENAI_API_KEY:
            raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def gerar_resposta(self, mensagens: List[Dict[str, str]], model_name: str, max_tokens: int) -> str:
        """Gera resposta usando a API da OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=mensagens,
                temperature=0.5,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"ERRO: Falha na chamada à API da OpenAI. Causa: {type(e).__name__}: {e}")
            raise RuntimeError(f"Erro ao comunicar com a OpenAI: {type(e).__name__}: {e}") from e