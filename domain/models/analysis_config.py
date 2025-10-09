from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class AnalysisConfig:
    model_name: str
    max_tokens: int
    temperature: float = 0.5
    top_p: Optional[float] = None
    stop_sequences: Optional[list] = None

    def __post_init__(self):
        if not self.model_name or not isinstance(self.model_name, str):
            raise ValueError('model_name deve ser uma string não vazia')
        if self.max_tokens <= 0:
            raise ValueError('max_tokens deve ser maior que zero')
        if not (0 <= self.temperature <= 2):
            raise ValueError('temperature deve estar entre 0 e 2')
