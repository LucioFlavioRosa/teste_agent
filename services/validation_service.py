from typing import Optional

class ValidationService:
    analises_validas = ["design", "pentest", "seguranca", "terraform"]

    def validate_analysis_type(self, tipo_analise: str):
        if tipo_analise not in self.analises_validas:
            raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {self.analises_validas}")

    def validate_input_sources(self, repositorio: Optional[str], codigo: Optional[str]):
        if repositorio is None and codigo is None:
            raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")
