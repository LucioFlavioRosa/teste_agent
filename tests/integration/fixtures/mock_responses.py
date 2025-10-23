import pytest

@pytest.fixture
def github_file_structure():
    return {
        'agents/agente_revisor.py': 'conteudo do agente',
        'tools/github_reader.py': 'conteudo do github_reader',
    }

@pytest.fixture
def github_api_success_response():
    return {
        'status_code': 200,
        'json': lambda: {
            'content': 'ZmlsZSBjb250ZW50',  # base64 de 'file content'
            'encoding': 'base64',
        }
    }

@pytest.fixture
def github_api_rate_limit_response():
    return {
        'status_code': 403,
        'json': lambda: {'message': 'API rate limit exceeded'}
    }

@pytest.fixture
def openai_api_success_response():
    return {
        'choices': [
            {'message': {'content': 'Análise de teste.'}}
        ]
    }

@pytest.fixture
def openai_api_error_429_response():
    return {
        'error': {
            'message': 'Rate limit exceeded',
            'type': 'rate_limit',
            'code': 429
        }
    }
