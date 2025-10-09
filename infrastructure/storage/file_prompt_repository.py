import os
from infrastructure.storage.prompt_repository_interface import IPromptRepository

class FilePromptRepository(IPromptRepository):
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(__file__), '../../tools/prompt')
        self.base_dir = os.path.abspath(base_dir)

    def get_prompt(self, tipo_analise: str) -> str:
        caminho_prompt = os.path.join(self.base_dir, f'{tipo_analise}.md')
        try:
            with open(caminho_prompt, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError as e:
            raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}") from e
