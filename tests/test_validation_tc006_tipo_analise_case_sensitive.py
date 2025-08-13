import pytest
from agents.agente_revisor import validation

def test_validation_tipo_analise_case_sensitive():
    with pytest.raises(ValueError) as exc:
        validation(tipo_analise='DeSiGn', repositorio='org/repo', codigo=None)
    assert "Tipo de análise 'DeSiGn' é inválido" in str(exc.value)
