import pytest
from agents import agente_revisor


def test_validation_tipo_invalido():
    with pytest.raises(ValueError):
        agente_revisor.validation(tipo_analise='invalido', repositorio='owner/repo')


def test_validation_sem_fonte():
    with pytest.raises(ValueError):
        agente_revisor.validation(tipo_analise='pentest')


def test_main_com_codigo_e_llm_injetado():
    def fake_llm_runner(**kwargs):
        assert kwargs['tipo_analise'] == 'pentest'
        assert 'print(' in kwargs['codigo']
        return 'OK'

    resultado = agente_revisor.executar_analise(
        tipo_analise='pentest',
        codigo="print('hello')",
        llm_runner=fake_llm_runner,
    )

    assert resultado['tipo_analise'] == 'pentest'
    assert resultado['resultado'] == 'OK'


def test_main_usa_code_fetcher_injetado():
    def fake_fetcher(repositorio, tipo_analise, **kwargs):
        assert repositorio == 'owner/repo'
        assert tipo_analise == 'pentest'
        return {'file.py': 'print(42)'}

    def fake_llm_runner(**kwargs):
        # O código chega como str(); dicionários são transformados em string
        assert 'file.py' in kwargs['codigo']
        return 'ANALISE_FALSA'

    resultado = agente_revisor.executar_analise(
        tipo_analise='pentest',
        repositorio='owner/repo',
        code_fetcher=fake_fetcher,
        llm_runner=fake_llm_runner,
    )

    assert resultado['tipo_analise'] == 'pentest'
    assert resultado['resultado'] == 'ANALISE_FALSA'
