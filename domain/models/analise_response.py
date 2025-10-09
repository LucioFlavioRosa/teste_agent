from pydantic import BaseModel, Field
from typing import Any, Dict
from datetime import datetime

class AnaliseResponse(BaseModel):
    conteudo: str = Field(...)
    tokens_usados: int = Field(default=0)
    modelo_utilizado: str = Field(default='')
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadados: Dict[str, Any] = Field(default_factory=dict)
