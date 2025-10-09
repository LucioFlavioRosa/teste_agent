import os

class LLMConfig:
    def __init__(self, model_name: str, temperature: float, max_tokens: int, api_key_source: str = 'env'):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key_source = api_key_source

    @classmethod
    def from_env(cls):
        model_name = os.getenv('LLM_MODEL_NAME', 'gpt-3.5-turbo')
        temperature = float(os.getenv('LLM_TEMPERATURE', '0.5'))
        max_tokens = int(os.getenv('LLM_MAX_TOKENS', '2048'))
        api_key_source = os.getenv('LLM_API_KEY_SOURCE', 'env')
        return cls(model_name, temperature, max_tokens, api_key_source)

    def validate(self):
        if not self.model_name:
            raise ValueError('Model name não pode ser vazio.')
        if not (0 <= self.temperature <= 2):
            raise ValueError('Temperature deve estar entre 0 e 2.')
        if self.max_tokens <= 0:
            raise ValueError('max_tokens deve ser positivo.')
