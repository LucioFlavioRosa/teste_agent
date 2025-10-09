import os

class APIKeyProvider:
    def get_api_key(self, service_name: str) -> str:
        raise NotImplementedError

class ColabAPIKeyProvider(APIKeyProvider):
    def __init__(self):
        from google.colab import userdata
        self.userdata = userdata
    def get_api_key(self, service_name: str) -> str:
        key = self.userdata.get(f'{service_name.upper()}_API_KEY')
        if not key:
            raise ValueError(f'Chave da API para {service_name} não encontrada no Colab.')
        return key

class EnvironmentAPIKeyProvider(APIKeyProvider):
    def get_api_key(self, service_name: str) -> str:
        key = os.environ.get(f'{service_name.upper()}_API_KEY')
        if not key:
            raise ValueError(f'Chave da API para {service_name} não encontrada nas variáveis de ambiente.')
        return key
