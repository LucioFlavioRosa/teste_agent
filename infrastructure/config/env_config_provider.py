import os

class EnvConfigProvider:
    def get_secret(self, key: str) -> str:
        return os.getenv(key)
    def get_config(self, key: str, default=None):
        value = os.getenv(key)
        return value if value is not None else default
