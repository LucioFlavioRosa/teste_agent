import pytest
from unittest.mock import patch
from agents.agente_revisor import validation

def test_validation_caminho_feliz_com_repositorio():
    with patch('agents.agente_revisor.code_from_repo', return_value={'foo.py': 'print(123)'}) as mock_code:
        result = validation(tipo_analise='design', repositorio='org/repo', codigo=None)
        assert result == {'foo.py': 'print(123)'}
        mock_code.assert_called_once_with(tipo_analise='design', repositorio='org/repo')
