import os
import pytest
from unittest.mock import patch, mock_open, MagicMock
from openai import OpenAI

# Importar o módulo sob teste
from tools.revisor_geral import carregar_prompt, executar_analise_llm


class TestCarregarPrompt:
    """Testes para a função carregar_prompt"""
    
    @patch('builtins.open', new_callable=mock_open, read_data='Conteúdo do prompt de teste')
    @patch('os.path.join')
    @patch('os.path.dirname')
    def test_carregar_prompt_arquivo_existe(self, mock_dirname, mock_join, mock_file):
        """Testa se carregar_prompt retorna o conteúdo correto quando o arquivo existe"""
        # Arrange
        mock_dirname.return_value = '/fake/path'
        mock_join.return_value = '/fake/path/prompts/analise_teste.md'
        tipo_analise = 'analise_teste'
        
        # Act
        resultado = carregar_prompt(tipo_analise)
        
        # Assert
        assert resultado == 'Conteúdo do prompt de teste'
        mock_file.assert_called_once_with('/fake/path/prompts/analise_teste.md', 'r', encoding='utf-8')
        mock_join.assert_called_once_with('/fake/path', 'prompts', 'analise_teste.md')
    
    @patch('builtins.open', side_effect=FileNotFoundError('Arquivo não encontrado'))
    @patch('os.path.join')
    @patch('os.path.dirname')
    def test_carregar_prompt_arquivo_inexistente(self, mock_dirname, mock_join, mock_file):
        """Testa se carregar_prompt lança ValueError quando o arquivo não existe"""
        # Arrange
        mock_dirname.return_value = '/fake/path'
        mock_join.return_value = '/fake/path/prompts/inexistente.md'
        tipo_analise = 'inexistente'
        
        # Act & Assert
        with pytest.raises(ValueError, match="Arquivo de prompt para a análise 'inexistente' não encontrado"):
            carregar_prompt(tipo_analise)


class TestExecutarAnaliseLLM:
    """Testes para a função executar_analise_llm"""
    
    @patch('tools.revisor_geral.carregar_prompt')
    @patch('tools.revisor_geral.openai_client')
    def test_executar_analise_llm_chamada_openai_mockada(self, mock_openai_client, mock_carregar_prompt):
        """Testa o fluxo principal de executar_analise_llm com mock da OpenAI"""
        # Arrange
        mock_carregar_prompt.return_value = 'Prompt do sistema de teste'
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '  Resposta da análise  '
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        tipo_analise = 'teste'
        codigo = 'def teste(): pass'
        analise_extra = 'Instruções extras'
        model_name = 'gpt-4'
        max_token_out = 1000
        
        # Act
        resultado = executar_analise_llm(tipo_analise, codigo, analise_extra, model_name, max_token_out)
        
        # Assert
        assert resultado == 'Resposta da análise'
        mock_carregar_prompt.assert_called_once_with('teste')
        mock_openai_client.chat.completions.create.assert_called_once_with(
            model='gpt-4',
            messages=[
                {"role": "system", "content": "Prompt do sistema de teste"},
                {'role': 'user', 'content': 'def teste(): pass'},
                {'role': 'user', 'content': 'Instruções extras do usuário a serem consideradas na análise: Instruções extras'}
            ],
            temperature=0.5,
            max_tokens=1000
        )
    
    @patch('tools.revisor_geral.carregar_prompt')
    @patch('tools.revisor_geral.openai_client')
    def test_executar_analise_llm_analise_extra_vazia(self, mock_openai_client, mock_carregar_prompt):
        """Testa executar_analise_llm quando analise_extra está vazia"""
        # Arrange
        mock_carregar_prompt.return_value = 'Prompt do sistema'
        mock_response = MagicMock()
        mock_response.choices[0].message.content = 'Resposta'
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Act
        resultado = executar_analise_llm('teste', 'codigo', '', 'gpt-4', 1000)
        
        # Assert
        expected_messages = [
            {"role": "system", "content": "Prompt do sistema"},
            {'role': 'user', 'content': 'codigo'},
            {'role': 'user', 'content': 'Nenhuma instrução extra fornecida pelo usuário.'}
        ]
        mock_openai_client.chat.completions.create.assert_called_once()
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args[1]['messages'] == expected_messages
    
    @patch('tools.revisor_geral.carregar_prompt')
    @patch('tools.revisor_geral.openai_client')
    @patch('builtins.print')
    def test_executar_analise_llm_erro_openai(self, mock_print, mock_openai_client, mock_carregar_prompt):
        """Testa se executar_analise_llm propaga RuntimeError quando há erro na OpenAI"""
        # Arrange
        mock_carregar_prompt.return_value = 'Prompt do sistema'
        mock_openai_client.chat.completions.create.side_effect = Exception('Erro de API')
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Erro ao comunicar com a OpenAI: Exception: Erro de API"):
            executar_analise_llm('teste', 'codigo', 'extra', 'gpt-4', 1000)
        
        # Verificar se o erro foi logado
        mock_print.assert_called_once_with(
            "ERRO: Falha na chamada à API da OpenAI para análise 'teste'. Causa: Exception: Erro de API"
        )


class TestInicializacaoModulo:
    """Testes para a inicialização do módulo"""
    
    @patch('tools.revisor_geral.userdata')
    def test_openai_api_key_ausente(self, mock_userdata):
        """Testa se o módulo lança ValueError quando OPENAI_API_KEY está ausente"""
        # Arrange
        mock_userdata.get.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="A chave da API da OpenAI não foi encontrada"):
            # Reimportar o módulo para simular a inicialização
            import importlib
            import tools.revisor_geral
            importlib.reload(tools.revisor_geral)
    
    @patch('tools.revisor_geral.userdata')
    @patch('tools.revisor_geral.OpenAI')
    def test_openai_api_key_presente(self, mock_openai_class, mock_userdata):
        """Testa se o módulo inicializa corretamente quando OPENAI_API_KEY está presente"""
        # Arrange
        mock_userdata.get.return_value = 'fake-api-key'
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Act
        import importlib
        import tools.revisor_geral
        importlib.reload(tools.revisor_geral)
        
        # Assert
        mock_userdata.get.assert_called_with('OPENAI_API_KEY')
        mock_openai_class.assert_called_with(api_key='fake-api-key')
