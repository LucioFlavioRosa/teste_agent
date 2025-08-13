import pytest
from unittest.mock import patch
from agents.agente_revisor import validation

def test_validation_repositorio_string_muito_longa():
    long_repo = 'a' * 10000
    with patch('agents.agente_revisor.code_from_repo', side_effect=RuntimeError('Falha ao executar a análise')) as mock_code:
        with pytest.raises(RuntimeError):
            validation(tipo_analise='design', repositorio=long_repo, codigo=None)
        mock_code.assert_called_once_with(tipo_analise='design', repositorio=long_repo)
