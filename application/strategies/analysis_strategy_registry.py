class AnalysisStrategyRegistry:
    def __init__(self):
        self._strategies = {}
    def register(self, analysis_type: str, file_extensions: list, prompt_path: str):
        self._strategies[analysis_type] = {'file_extensions': file_extensions, 'prompt_path': prompt_path}
    def get_strategy(self, analysis_type: str):
        return self._strategies.get(analysis_type)
