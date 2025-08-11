from typing import Optional
from tools import github_reader

class ValidationService:
    """
    Serviço responsável pela validação de parâmetros e obtenção do código para análise.
    """
    analises_validas = ["design", "pentest", "seguranca", "terraform"]

    def validate(self, tipo_analise: str,
                 repositorio: Optional[str] = None,
                 codigo: Optional[str] = None):
        if tipo_analise not in self.analises_validas:
            raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {self.analises_validas}")
        if repositorio is None and codigo is None:
            raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")
        if codigo is None:
            return github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo
