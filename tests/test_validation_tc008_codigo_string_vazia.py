import pytest
from agents.agente_revisor import validation

def test_validation_codigo_string_vazia():
    result = validation(tipo_analise='design', repositorio=None, codigo='')
    assert result == ''
