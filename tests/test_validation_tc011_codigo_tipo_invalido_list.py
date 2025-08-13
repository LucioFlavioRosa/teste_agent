import pytest
from agents.agente_revisor import validation

def test_validation_codigo_tipo_invalido_list():
    result = validation(tipo_analise='design', repositorio=None, codigo=[1,2,3])
    assert result == [1,2,3]
