from dataclasses import dataclass
from typing import Optional
from enum import Enum
from .analysis_config import AnalysisConfig

class TipoAnalise(Enum):
    DESIGN = 'design'
    PENTEST = 'pentest'
    SEGURANCA = 'seguranca'
    TERRAFORM = 'terraform'

@dataclass(frozen=True)
class AnalysisRequest:
    tipo_analise: str
    codigo: str
    instrucoes_extras: Optional[str]
    config: AnalysisConfig

    def __post_init__(self):
        if self.tipo_analise not in {item.value for item in TipoAnalise}:
            raise ValueError(f"tipo_analise inválido: {self.tipo_analise}")
        if not self.codigo or not isinstance(self.codigo, str):
            raise ValueError('codigo deve ser uma string não vazia')
