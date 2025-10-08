from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ILLMService(ABC):
    """Interface para serviços de LLM"""
    
    @abstractmethod
    def gerar_resposta(self, mensagens: List[Dict[str, str]], model_name: str, max_tokens: int) -> str:
        """Gera resposta usando o modelo LLM"""
        pass