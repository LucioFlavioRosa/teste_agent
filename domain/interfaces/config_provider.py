from typing import Protocol, Any

class IConfigProvider(Protocol):
    def get_secret(self, key: str) -> str:
        ...
    def get_config(self, key: str, default: Any = None) -> Any:
        ...
