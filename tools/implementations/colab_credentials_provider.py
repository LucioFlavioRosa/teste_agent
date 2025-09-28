from google.colab import userdata
from tools.interfaces.credentials_provider_interface import CredentialsProviderInterface

class ColabCredentialsProvider(CredentialsProviderInterface):
    def get_openai_api_key(self) -> str:
        return userdata.get('OPENAI_API_KEY')