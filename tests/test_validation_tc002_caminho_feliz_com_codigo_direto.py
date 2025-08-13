import pytest
from agents.agente_revisor import validation

def test_validation_caminho_feliz_com_codigo_direto():
    result = validation(tipo_analise='pentest', repositorio=None, codigo="print('ok')")
    assert result == "print('ok')"
