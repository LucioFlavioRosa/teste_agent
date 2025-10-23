import pytest
from tools import revisor_geral

class FakeOpenAIClient:
    class chat:
        class completions:
            @staticmethod
            def create(model, messages, temperature, max_tokens):
                return type('FakeResponse', (), {
                    'choices': [type('FakeChoice', (), {'message': type('FakeMsg', (), {'content': 'Resposta fake'})})]
                })()

def test_openai_success(monkeypatch):
    monkeypatch.setattr(revisor_geral, 'openai_client', FakeOpenAIClient())
    result = revisor_geral.executar_analise_llm(
        tipo_analise='design',
        codigo='codigo de teste',
        analise_extra='',
        model_name='fake-model',
        max_token_out=1000
    )
    assert isinstance(result, str)
    assert 'Resposta fake' in result

def test_openai_error(monkeypatch):
    class ErrorClient:
        class chat:
            class completions:
                @staticmethod
                def create(*args, **kwargs):
                    raise Exception('Erro 429')
    monkeypatch.setattr(revisor_geral, 'openai_client', ErrorClient())
    with pytest.raises(RuntimeError):
        revisor_geral.executar_analise_llm(
            tipo_analise='design',
            codigo='codigo de teste',
            analise_extra='',
            model_name='fake-model',
            max_token_out=1000
        )
