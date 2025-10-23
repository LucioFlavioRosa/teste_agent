import pytest
from tools import github_reader, revisor_geral
import logging

@pytest.mark.usefixtures('test_config')
def test_github_api_unavailable(monkeypatch, test_config):
    def fake_conectar_ao_github(*args, **kwargs):
        raise RuntimeError('GitHub API indisponível')
    monkeypatch.setattr(github_reader, 'conectar_ao_github', fake_conectar_ao_github)
    with pytest.raises(RuntimeError):
        github_reader.obter_arquivos_para_analise('repo/fake', 'python', config=test_config)

@pytest.mark.usefixtures('test_config')
def test_openai_rate_limit(monkeypatch):
    class ErrorClient:
        class chat:
            class completions:
                @staticmethod
                def create(*args, **kwargs):
                    raise Exception('429')
    monkeypatch.setattr(revisor_geral, 'openai_client', ErrorClient())
    with pytest.raises(RuntimeError):
        revisor_geral.executar_analise_llm(
            tipo_analise='design',
            codigo='codigo',
            analise_extra='',
            model_name='fake',
            max_token_out=100
        )

def test_prompt_file_not_found(monkeypatch):
    monkeypatch.setattr(revisor_geral, 'carregar_prompt', lambda tipo_analise: (_ for _ in ()).throw(ValueError('Arquivo de prompt não encontrado')))
    with pytest.raises(ValueError):
        revisor_geral.executar_analise_llm(
            tipo_analise='design',
            codigo='codigo',
            analise_extra='',
            model_name='fake',
            max_token_out=100
        )
