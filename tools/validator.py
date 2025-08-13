def validar_tipo_analise(tipo_analise: str, analises_validas: list):
    """
    Valida se o tipo de análise está entre os tipos válidos.
    """
    if tipo_analise not in analises_validas:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {analises_validas}")

def validar_parametros_entrada(repositorio, codigo):
    """
    Garante que pelo menos um dos parâmetros (repositorio ou codigo) foi fornecido.
    """
    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")
