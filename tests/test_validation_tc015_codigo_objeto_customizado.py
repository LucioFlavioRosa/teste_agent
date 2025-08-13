import pytest
from agents.agente_revisor import validation

def test_validation_codigo_objeto_customizado():
    obj = object()
    result = validation(tipo_analise='design', repositorio=None, codigo=obj)
    assert result == obj
