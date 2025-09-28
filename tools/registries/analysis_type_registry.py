from typing import Dict, List

class AnalysisTypeRegistry:
    def __init__(self):
        self._registry = {
            "terraform": [".tf", ".tfvars"],
            "python": [".py"],
            "cloudformation": [".json", ".yaml", ".yml"],
            "ansible": [".yml", ".yaml"],
            "docker": ["Dockerfile"],
        }
    
    def register_analysis_type(self, analysis_type: str, extensions: List[str]):
        self._registry[analysis_type.lower()] = extensions
    
    def get_extensions(self, analysis_type: str) -> List[str]:
        return self._registry.get(analysis_type.lower())
    
    def get_all_types(self) -> List[str]:
        return list(self._registry.keys())