import pytest
from agents import agente_revisor

class FakeGithubReader:
    @staticmethod
    def obter_arquivos_para_analise(repo_nome, tipo_analise, **kwargs):
        return {'fake.py': 'print("hello")'}

class FakeRevisorGeral:
    @staticmethod
    def executar_analise_llm(tipo_analise, codigo, analise_extra, model_name, max_token_out):
        return 'Resultado final de teste.'

def test_end_to_end(monkeypatch, test_config):
    monkeypatch.setattr('tools.github_reader', 'obter_arquivos_para_analise', FakeGithubReader.obter_arquivos_para_analise)
    monkeypatch.setattr('tools.revisor_geral', 'executar_analise_llm', FakeRevisorGeral.executar_analise_llm)
    resultado = agente_revisor.executar_analise(
        tipo_analise='design',
        repositorio='fake/repo',
        config=test_config
    )
    assert isinstance(resultado, dict)
    assert 'tipo_analise' in resultado
    assert 'resultado' in resultado
    assert isinstance(resultado['resultado'], str) and resultado['resultado']
