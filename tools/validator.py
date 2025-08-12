class AnaliseValidator:
    """Classe utilitária para validação de parâmetros de análise."""
    analises_validas = ["design", "pentest", "seguranca", "terraform"]

    @staticmethod
    def validar_tipo_analise(tipo_analise: str):
        if tipo_analise not in AnaliseValidator.analises_validas:
            raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {AnaliseValidator.analises_validas}")

    @staticmethod
    def validar_origem_codigo(repositorio, codigo):
        if repositorio is None and codigo is None:
            raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")
