import pytest
from agents.agente_revisor import validation

def test_validation_codigo_unicode():
    unicode_str = "✓🚀"
    result = validation(tipo_analise='design', repositorio=None, codigo=unicode_str)
    assert result == unicode_str
