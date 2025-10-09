from typing import Protocol, Dict, Any

class ICodeRepository(Protocol):
    def fetch_code(self, repo_name: str, filters: Dict[str, Any]) -> Dict[str, str]:
        ...
    def is_available(self) -> bool:
        ...
