import os

class PromptLoader:
    """Classe responsável pelo carregamento de prompts"""
    
    def carregar_prompt(self, tipo_analise: str) -> str:
        """Carrega o prompt para o tipo de análise especificado"""
        caminho_prompt = os.path.join(os.path.dirname(__file__), '..', 'tools', 'prompts', f'{tipo_analise}.md')
        try:
            with open(caminho_prompt, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError as e:
            raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}") from e