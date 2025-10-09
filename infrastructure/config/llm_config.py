import os

DEFAULT_MODEL = os.getenv('LLM_DEFAULT_MODEL', 'gpt-3.5-turbo')
DEFAULT_MAX_TOKENS = int(os.getenv('LLM_DEFAULT_MAX_TOKENS', '2048'))
DEFAULT_TEMPERATURE = float(os.getenv('LLM_DEFAULT_TEMPERATURE', '0.5'))
API_TIMEOUT = int(os.getenv('LLM_API_TIMEOUT', '60'))
RETRY_ATTEMPTS = int(os.getenv('LLM_RETRY_ATTEMPTS', '3'))
