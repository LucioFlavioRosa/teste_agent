import os
from typing import Dict

class PromptLoaderService:
    def __init__(self):
        self._cache: Dict[str, str] = {}
        self._base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'prompt')

    def load_prompt(self, tipo_analise: str) -> str:
        if tipo_analise in self._cache:
            return self._cache[tipo_analise]
        caminho_prompt = os.path.join(self._base_dir, f'{tipo_analise}.md')
        if not os.path.isfile(caminho_prompt):
            raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            self._cache[tipo_analise] = conteudo
            return conteudo
