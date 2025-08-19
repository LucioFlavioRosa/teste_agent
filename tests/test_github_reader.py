import pytest
from tools.github_reader import conection


def test_conection_com_token_invalido(mocker):
    mocker.patch('google.colab.userdata.get', return_value=None)
    with pytest.raises(ValueError, match="A chave da API da OpenAI não foi encontrada."):
        conection('some/repo')
