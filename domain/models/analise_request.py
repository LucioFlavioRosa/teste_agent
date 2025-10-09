from pydantic import BaseModel, Field, validator
from infrastructure.config.llm_config import DEFAULT_MODEL, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE

TIPOS_ANALISE_PERMITIDOS = ['design', 'pentest', 'seguranca', 'terraform']

class AnaliseRequest(BaseModel):
    tipo_analise: str = Field(...)
    codigo: str = Field(...)
    analise_extra: str = Field(default='')
    model_name: str = Field(default=DEFAULT_MODEL)
    max_token_out: int = Field(default=DEFAULT_MAX_TOKENS)
    temperature: float = Field(default=DEFAULT_TEMPERATURE)

    @validator('tipo_analise')
    def tipo_analise_valido(cls, v):
        if v not in TIPOS_ANALISE_PERMITIDOS:
            raise ValueError(f"tipo_analise deve ser um dos: {TIPOS_ANALISE_PERMITIDOS}")
        return v

    @validator('max_token_out')
    def max_token_positivo(cls, v):
        if v <= 0:
            raise ValueError("max_token_out deve ser maior que zero")
        return v
