from typing import Protocol, List, Dict, Optional


class ILLMClient(Protocol):
    def chat(self, messages: List[Dict[str, str]], model: str, max_tokens: int, temperature: float) -> str:
        ...


class PromptRepository(Protocol):
    def load_prompt(self, tipo_analise: str) -> str:
        ...

    def list_types(self) -> List[str]:
        ...


class SecretsProvider(Protocol):
    def get(self, key: str) -> Optional[str]:
        ...


class IFileFilter(Protocol):
    def should_read(self, path: str, name: str) -> bool:
        ...


class ICodeRepositoryReader(Protocol):
    def read_repo(self, repositorio: str, file_filter: IFileFilter) -> Dict[str, str]:
        ...
