import pytest
from agents.agente_revisor import validation

def test_validation_ambos_presentes_codigo_precede():
    result = validation(tipo_analise='seguranca', repositorio='org/repo', codigo='print(1)')
    assert result == 'print(1)'
