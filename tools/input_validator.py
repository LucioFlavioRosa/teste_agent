def validar_parametros_entrada(tipo_analise, repositorio, caminho_credenciais):
    """
    Valida os parâmetros de entrada para o agente revisor.
    Args:
        tipo_analise (str): Tipo de análise a ser realizada.
        repositorio (str): Endereço do repositório a ser analisado.
        caminho_credenciais (str): Caminho para as credenciais do Github.
    Returns:
        tuple: (bool, str) indicando se os parâmetros são válidos e uma mensagem.
    """
    if not tipo_analise:
        return False, "Tipo de análise não informado."
    if not repositorio:
        return False, "Repositório não informado."
    if not caminho_credenciais:
        return False, "Caminho das credenciais não informado."
    return True, ""
