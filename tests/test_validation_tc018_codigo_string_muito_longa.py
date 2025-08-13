import pytest
from agents.agente_revisor import validation

def test_validation_codigo_string_muito_longa():
    long_code = 'a' * 10000
    result = validation(tipo_analise='design', repositorio=None, codigo=long_code)
    assert result == long_code
