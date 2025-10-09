from google.colab import userdata

class ColabConfigProvider:
    def get_secret(self, key: str) -> str:
        return userdata.get(key)
    def get_config(self, key: str, default=None):
        value = userdata.get(key)
        return value if value is not None else default
