import pytest
from agents.agente_revisor import validation

def test_validation_tipo_analise_none():
    with pytest.raises(ValueError) as exc:
        validation(tipo_analise=None, repositorio='org/repo', codigo=None)
    assert "Tipo de análise 'None' é inválido" in str(exc.value)
