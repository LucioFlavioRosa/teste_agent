import pytest
from agents.agente_revisor import validation

def test_validation_tipo_analise_string_longa():
    tipo_analise = 'd' * 1000
    with pytest.raises(ValueError) as exc:
        validation(tipo_analise=tipo_analise, repositorio='org/repo', codigo=None)
    assert f"Tipo de análise '{tipo_analise}' é inválido" in str(exc.value)
