from typing import Any, List, Dict
from openai import OpenAI
from .llm_client_interface import LLMClientInterface

class OpenAIClientAdapter(LLMClientInterface):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def chat_completion(self, messages: List[Dict[str, Any]], model: str, temperature: float, max_tokens: int, **kwargs) -> Dict[str, Any]:
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return {
            'content': response.choices[0].message.content.strip(),
            'usage': getattr(response, 'usage', None),
            'model': model
        }
