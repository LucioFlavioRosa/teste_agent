import os

class PromptLoader:
    def __init__(self, base_path):
        self.base_path = base_path
    def load_prompt(self, analysis_type: str) -> str:
        path = os.path.join(self.base_path, f'{analysis_type}.md')
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
