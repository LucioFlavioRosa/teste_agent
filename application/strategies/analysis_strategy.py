from typing import Protocol, List

class AnalysisStrategy(Protocol):
    def get_file_extensions(self) -> List[str]:
        ...
    def get_prompt_path(self) -> str:
        ...
