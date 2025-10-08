import pytest
from unittest.mock import patch, MagicMock
import tools.github_reader as github_reader

# Teste 1: test_conection_with_valid_token
@patch('tools.github_reader.userdata.get')
@patch('tools.github_reader.Github')
def test_conection_with_valid_token(mock_github, mock_userdata_get):
    mock_userdata_get.return_value = 'valid_token'
    mock_repo = MagicMock()
    mock_github.return_value.get_repo.return_value = mock_repo
    repo = github_reader.conection('user/repo')
    assert repo == mock_repo
    mock_github.assert_called()
    mock_github.return_value.get_repo.assert_called_with('user/repo')

# Teste 2: test_conection_raises_exception_with_invalid_token
@patch('tools.github_reader.userdata.get')
@patch('tools.github_reader.Github')
def test_conection_raises_exception_with_invalid_token(mock_github, mock_userdata_get):
    mock_userdata_get.return_value = None
    mock_github.side_effect = Exception('Invalid token')
    with pytest.raises(Exception):
        github_reader.conection('user/repo')

# Teste 3: test_leitura_recursiva_com_extensoes_especificas
@patch('tools.github_reader.Github')
def test_leitura_recursiva_com_extensoes_especificas(mock_github):
    repo = MagicMock()
    file_py = MagicMock()
    file_py.type = 'file'
    file_py.path = 'src/main.py'
    file_py.name = 'main.py'
    file_py.decoded_content = b'print("hello")'
    dir_obj = MagicMock()
    dir_obj.type = 'dir'
    dir_obj.path = 'src'
    repo.get_contents.side_effect = lambda path='': [file_py] if path == '' else []
    extensoes = ['.py']
    result = github_reader._leitura_recursiva_com_debug(repo, extensoes)
    assert 'src/main.py' in result
    assert result['src/main.py'] == 'print("hello")'

# Teste 4: test_leitura_recursiva_sem_filtro_extensao
@patch('tools.github_reader.Github')
def test_leitura_recursiva_sem_filtro_extensao(mock_github):
    repo = MagicMock()
    file_py = MagicMock()
    file_py.type = 'file'
    file_py.path = 'src/main.py'
    file_py.name = 'main.py'
    file_py.decoded_content = b'print("hello")'
    file_tf = MagicMock()
    file_tf.type = 'file'
    file_tf.path = 'infra/main.tf'
    file_tf.name = 'main.tf'
    file_tf.decoded_content = b'resource "aws_s3_bucket" "b" {}'
    repo.get_contents.return_value = [file_py, file_tf]
    result = github_reader._leitura_recursiva_com_debug(repo, None)
    assert 'src/main.py' in result
    assert 'infra/main.tf' in result

# Teste 5: test_leitura_recursiva_com_arquivo_nao_decodificavel
@patch('tools.github_reader.Github')
def test_leitura_recursiva_com_arquivo_nao_decodificavel(mock_github, capsys):
    repo = MagicMock()
    file_bad = MagicMock()
    file_bad.type = 'file'
    file_bad.path = 'src/bad.py'
    file_bad.name = 'bad.py'
    def raise_decode():
        raise UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')
    file_bad.decoded_content.decode.side_effect = raise_decode
    repo.get_contents.return_value = [file_bad]
    result = github_reader._leitura_recursiva_com_debug(repo, ['.py'])
    assert result == {}
    captured = capsys.readouterr()
    assert "DEBUG: ERRO na decodificação" in captured.out

# Teste 6: test_leitura_recursiva_com_diretorio_vazio
@patch('tools.github_reader.Github')
def test_leitura_recursiva_com_diretorio_vazio(mock_github):
    repo = MagicMock()
    repo.get_contents.return_value = []
    result = github_reader._leitura_recursiva_com_debug(repo, ['.py'])
    assert result == {}

# Teste 7: test_main_retorna_arquivos_corretos_para_tipo_python
@patch('tools.github_reader.conection')
@patch('tools.github_reader._leitura_recursiva_com_debug')
def test_main_retorna_arquivos_corretos_para_tipo_python(mock_leitura, mock_conection):
    mock_repo = MagicMock()
    mock_conection.return_value = mock_repo
    mock_leitura.return_value = {'src/main.py': 'print("hello")', 'src/utils.py': 'def x(): pass'}
    result = github_reader.main('user/repo', 'python')
    assert 'src/main.py' in result
    assert 'src/utils.py' in result
    mock_leitura.assert_called_with(mock_repo, ['.py'])

# Teste 8: test_main_com_tipo_analise_invalido
@patch('tools.github_reader.conection')
@patch('tools.github_reader._leitura_recursiva_com_debug')
def test_main_com_tipo_analise_invalido(mock_leitura, mock_conection):
    mock_repo = MagicMock()
    mock_conection.return_value = mock_repo
    mock_leitura.return_value = {'src/main.py': 'print("hello")', 'infra/main.tf': 'resource "aws_s3_bucket" "b" {}'}
    result = github_reader.main('user/repo', 'nao_existente')
    assert 'src/main.py' in result
    assert 'infra/main.tf' in result
    mock_leitura.assert_called_with(mock_repo, None)
