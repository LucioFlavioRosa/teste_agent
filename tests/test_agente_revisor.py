import pytest
from agents.agente_revisor import code_from_repo, validation


def test_code_from_repo_valid(mocker):
    mocker.patch('tools.github_reader.main', return_value='mocked_code')
    result = code_from_repo('valid/repo', 'design')
    assert result == 'mocked_code'


def test_code_from_repo_invalid(mocker):
    mocker.patch('tools.github_reader.main', side_effect=RuntimeError('Falha ao executar a análise de design'))
    with pytest.raises(RuntimeError, match="Falha ao executar a análise de 'design'"):
        code_from_repo('invalid/repo', 'design')


def test_validation_tipo_analise_invalido():
    with pytest.raises(ValueError, match="Tipo de análise 'invalido' é inválido."):
        validation(tipo_analise='invalido')


def test_validation_sem_repositorio_ou_codigo():
    with pytest.raises(ValueError, match="Erro: É obrigatório fornecer 'repositorio' ou 'codigo'."):
        validation(tipo_analise='design')
