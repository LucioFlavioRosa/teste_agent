import pytest
from agents.agente_revisor import validation

def test_validation_tipo_analise_invalido():
    with pytest.raises(ValueError) as exc:
        validation(tipo_analise='foo', repositorio='org/repo', codigo=None)
    assert "Tipo de análise 'foo' é inválido" in str(exc.value)
