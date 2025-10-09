from typing import Union, Dict

class AnalysisRequest:
    def __init__(self, analysis_type: str, code_source: Union[str, Dict], extra_instructions: str, model_name: str, max_tokens: int):
        self.analysis_type = analysis_type
        self.code_source = code_source
        self.extra_instructions = extra_instructions
        self.model_name = model_name
        self.max_tokens = max_tokens
