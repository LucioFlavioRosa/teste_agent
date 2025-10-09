import os
from functools import lru_cache

class PromptLoaderService:
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(__file__), '../../tools/prompts')
        self.base_dir = os.path.abspath(base_dir)

    @lru_cache(maxsize=32)
    def load_prompt(self, tipo_analise):
        caminho_prompt = os.path.join(self.base_dir, f'{tipo_analise}.md')
        if not os.path.isfile(caminho_prompt):
            raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
