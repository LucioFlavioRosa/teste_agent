import os
try:
    from google.colab import userdata
except ImportError:
    userdata = None

def obter_github_token():
    """
    Abstrai a obtenção do token do GitHub, seja via Colab ou variável de ambiente.
    """
    if userdata is not None:
        token = userdata.get('github_token')
        if token:
            return token
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        return token
    raise ValueError("Token do GitHub não encontrado em Colab nem variável de ambiente.")

def obter_openai_api_key():
    """
    Abstrai a obtenção da chave da API OpenAI, seja via Colab ou variável de ambiente.
    """
    if userdata is not None:
        key = userdata.get('OPENAI_API_KEY')
        if key:
            return key
    key = os.environ.get('OPENAI_API_KEY')
    if key:
        return key
    raise ValueError("Chave da API da OpenAI não encontrada em Colab nem variável de ambiente.")
