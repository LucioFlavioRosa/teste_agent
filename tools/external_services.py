import os

try:
    from google.colab import userdata
except ImportError:
    userdata = None

def obter_token_github():
    """
    Obtém o token do Github, preferencialmente do ambiente Colab.
    """
    if userdata:
        return userdata.get('GITHUB_TOKEN')
    return os.environ.get('GITHUB_TOKEN')

def obter_token_openai():
    """
    Obtém o token da OpenAI, preferencialmente do ambiente Colab.
    """
    if userdata:
        return userdata.get('OPENAI_API_KEY')
    return os.environ.get('OPENAI_API_KEY')
