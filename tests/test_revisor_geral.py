import pytest
from unittest.mock import patch, mock_open, MagicMock
import tools.revisor_geral as revisor_geral

# Teste 1: test_carregar_prompt_arquivo_existente
@patch('builtins.open', new_callable=mock_open, read_data='conteudo do prompt')
@patch('os.path.dirname')
def test_carregar_prompt_arquivo_existente(mock_dirname, mock_file):
    mock_dirname.return_value = '/fake/path'
    tipo_analise = 'design'
    result = revisor_geral.carregar_prompt(tipo_analise)
    assert result == 'conteudo do prompt'

# Teste 2: test_carregar_prompt_arquivo_nao_encontrado
@patch('builtins.open', side_effect=FileNotFoundError)
@patch('os.path.dirname')
def test_carregar_prompt_arquivo_nao_encontrado(mock_dirname, mock_file):
    mock_dirname.return_value = '/fake/path'
    tipo_analise = 'inexistente'
    with pytest.raises(ValueError) as excinfo:
        revisor_geral.carregar_prompt(tipo_analise)
    assert "Arquivo de prompt para a análise" in str(excinfo.value)

# Teste 3: test_executar_analise_llm_com_resposta_valida
@patch('tools.revisor_geral.openai_client')
@patch('tools.revisor_geral.carregar_prompt', return_value='PROMPT')
def test_executar_analise_llm_com_resposta_valida(mock_carregar_prompt, mock_openai_client):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = 'resposta da openai'
    mock_openai_client.chat.completions.create.return_value = mock_response
    result = revisor_geral.executar_analise_llm('design', 'codigo', 'extra', 'gpt-4', 100)
    assert result == 'resposta da openai'
    mock_openai_client.chat.completions.create.assert_called()

# Teste 4: test_executar_analise_llm_com_falha_api
@patch('tools.revisor_geral.openai_client')
@patch('tools.revisor_geral.carregar_prompt', return_value='PROMPT')
def test_executar_analise_llm_com_falha_api(mock_carregar_prompt, mock_openai_client):
    mock_openai_client.chat.completions.create.side_effect = Exception('API error')
    with pytest.raises(RuntimeError) as excinfo:
        revisor_geral.executar_analise_llm('design', 'codigo', 'extra', 'gpt-4', 100)
    assert "Erro ao comunicar com a OpenAI" in str(excinfo.value)

# Teste 5: test_executar_analise_llm_com_analise_extra_vazia
@patch('tools.revisor_geral.openai_client')
@patch('tools.revisor_geral.carregar_prompt', return_value='PROMPT')
def test_executar_analise_llm_com_analise_extra_vazia(mock_carregar_prompt, mock_openai_client):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = 'resposta'
    mock_openai_client.chat.completions.create.return_value = mock_response
    result = revisor_geral.executar_analise_llm('design', 'codigo', '', 'gpt-4', 100)
    assert result == 'resposta'
    args, kwargs = mock_openai_client.chat.completions.create.call_args
    mensagens = kwargs['messages'] if 'messages' in kwargs else args[1]
    assert any('Nenhuma instrução extra fornecida pelo usuário.' in m['content'] for m in mensagens)

# Teste 6: test_executar_analise_llm_com_parametros_customizados
@patch('tools.revisor_geral.openai_client')
@patch('tools.revisor_geral.carregar_prompt', return_value='PROMPT')
def test_executar_analise_llm_com_parametros_customizados(mock_carregar_prompt, mock_openai_client):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = 'resposta'
    mock_openai_client.chat.completions.create.return_value = mock_response
    revisor_geral.executar_analise_llm('design', 'codigo', 'extra', 'gpt-4', 123)
    mock_openai_client.chat.completions.create.assert_called()
    args, kwargs = mock_openai_client.chat.completions.create.call_args
    assert kwargs['model'] == 'gpt-4'
    assert kwargs['max_tokens'] == 123
    assert kwargs['temperature'] == 0.5

# Teste 7: test_openai_api_key_ausente
@patch('tools.revisor_geral.userdata.get', return_value=None)
def test_openai_api_key_ausente(mock_userdata_get):
    import importlib
    with pytest.raises(ValueError) as excinfo:
        importlib.reload(revisor_geral)
    assert "A chave da API da OpenAI não foi encontrada" in str(excinfo.value)
