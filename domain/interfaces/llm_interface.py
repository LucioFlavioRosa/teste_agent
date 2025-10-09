from typing import List, Dict

class ILLMProvider:
    def executar_analise(self, prompt_sistema: str, mensagens: List[Dict], model_name: str, max_tokens: int) -> str:
        raise NotImplementedError