import os

class PromptLoader:
    def __init__(self, prompts_dir):
        self.prompts_dir = prompts_dir
        self._cache = {}

    def load(self, analysis_type: str) -> str:
        if analysis_type in self._cache:
            return self._cache[analysis_type]
        prompt_path = os.path.join(self.prompts_dir, f"{analysis_type}.md")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self._cache[analysis_type] = content
        return content
