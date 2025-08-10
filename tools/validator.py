def validar_parametros(tipo_analise, repositorio):
    """
    Valida os parâmetros de entrada da análise.

    Args:
        tipo_analise (str): Tipo de análise.
        repositorio (str): URL do repositório.

    Raises:
        ValueError: Se algum parâmetro for inválido.
    """
    analises_validas = ['design', 'pentest', 'documentacao']
    if tipo_analise not in analises_validas:
        raise ValueError('Tipo de análise inválido.')
    if not isinstance(repositorio, str) or not repositorio:
        raise ValueError('Repositório inválido.')
