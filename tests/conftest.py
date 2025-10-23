import pytest
import os

@pytest.fixture(scope='session', autouse=True)
def set_test_env_vars(monkeypatch):
    # Define variáveis de ambiente fake para testes
    monkeypatch.setenv('GITHUB_TOKEN', 'fake-github-token')
    monkeypatch.setenv('OPENAI_API_KEY', 'fake-openai-key')

@pytest.fixture(scope='session')
def test_config():
    # Configuração centralizada para injeção em componentes
    from agents.agente_revisor import Config
    return Config(github_token='fake-github-token', openai_api_key='fake-openai-key')
