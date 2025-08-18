import os
import logging

def get_secret(key: str):
    """Obtém segredo de os.environ ou do Colab se disponível."""
    valor = os.environ.get(key)
    if valor:
        return valor
    try:
        import google.colab
        from google.colab import userdata
        valor = userdata.get(key)
        if valor:
            return valor
    except ImportError:
        logging.debug("google.colab não disponível para leitura do segredo %s", key)
    except Exception as e:
        logging.error(f"Erro ao tentar obter segredo '{key}' do Colab: {e}")
    return None
