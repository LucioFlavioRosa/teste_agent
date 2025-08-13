import pytest
from agents.agente_revisor import validation

def test_validation_ambos_repositorio_e_codigo_ausentes():
    with pytest.raises(ValueError) as exc:
        validation(tipo_analise='design', repositorio=None, codigo=None)
    assert "obrigatório fornecer 'repositorio' ou 'codigo'" in str(exc.value)
