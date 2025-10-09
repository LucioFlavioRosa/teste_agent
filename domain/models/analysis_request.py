from typing import Optional, Dict, Any, Union
from domain.value_objects.file_filter import FileFilter

class RepositorySource:
    def __init__(self, repo_name: str, file_filter: FileFilter):
        self.repo_name = repo_name
        self.file_filter = file_filter

class DirectCodeSource:
    def __init__(self, code: Union[str, Dict[str, str]]):
        self.code = code

class AnalysisRequest:
    def __init__(self, analysis_type: str, code_source: Union[RepositorySource, DirectCodeSource], extra_instructions: str = '', llm_config: Optional[Dict[str, Any]] = None):
        self.analysis_type = analysis_type
        self.code_source = code_source
        self.extra_instructions = extra_instructions
        self.llm_config = llm_config or {}
