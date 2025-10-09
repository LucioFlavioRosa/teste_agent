from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class AnalysisResult:
    conteudo: str
    tokens_usados: Optional[int]
    modelo_utilizado: Optional[str]
    tempo_execucao_ms: Optional[int]
    sucesso: bool
    erro: Optional[str]
