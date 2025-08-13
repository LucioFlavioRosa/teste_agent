import pytest
from agents.agente_revisor import validation

def test_validation_repositorio_none_codigo_none_tipo_analise_valido():
    with pytest.raises(ValueError) as exc:
        validation(tipo_analise='design', repositorio=None, codigo=None)
    assert "obrigatório fornecer 'repositorio' ou 'codigo'" in str(exc.value)
