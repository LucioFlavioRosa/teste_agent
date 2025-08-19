import pytest
from tools.revisor_geral import carregar_prompt


def test_carregar_prompt_arquivo_inexistente():
    with pytest.raises(ValueError, match="Arquivo de prompt para a análise 'inexistente' não encontrado"):
        carregar_prompt('inexistente')
