class ValidationService:
    @staticmethod
    def validar_tipo_analise(tipo_analise, tipos_validos):
        if tipo_analise not in tipos_validos:
            raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {tipos_validos}")
        return True

    @staticmethod
    def validar_entrada_codigo(repositorio_nome=None, codigo_entrada=None):
        if repositorio_nome is None and codigo_entrada is None:
            raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo_entrada'.")
        return True