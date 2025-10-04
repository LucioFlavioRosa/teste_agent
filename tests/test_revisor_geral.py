import pytest
import os
from unittest.mock import Mock, patch, mock_open
from tools.revisor_geral import carregar_prompt, executar_analise_llm


class TestRevisorGeral:
    """Testes unitários para o módulo revisor_geral.py"""

    @patch('tools.revisor_geral.userdata')
    def test_erro_ausencia_api_key(self, mock_userdata):
        """Testa se uma exceção é lançada quando OPENAI_API_KEY não está definida"""
        # Arrange
        mock_userdata.get.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="A chave da API da OpenAI não foi encontrada"):
            # Reimportar o módulo para forçar a execução da validação
            import importlib
            import tools.revisor_geral
            importlib.reload(tools.revisor_geral)

    @patch('builtins.open', side_effect=FileNotFoundError("Arquivo não encontrado"))
    @patch('os.path.join')
    @patch('os.path.dirname')
    def test_carregar_prompt_arquivo_inexistente(self, mock_dirname, mock_join, mock_open_file):
        """Testa se ValueError é lançado ao tentar carregar arquivo de prompt inexistente"""
        # Arrange
        mock_dirname.return_value = '/fake/path'
        mock_join.return_value = '/fake/path/prompts/inexistente.md'
        tipo_analise = 'inexistente'
        
        # Act & Assert
        with pytest.raises(ValueError, match="Arquivo de prompt para a análise 'inexistente' não encontrado"):
            carregar_prompt(tipo_analise)

    @patch('builtins.open', mock_open(read_data="Prompt de teste"))
    @patch('os.path.join')
    @patch('os.path.dirname')
    def test_carregar_prompt_sucesso(self, mock_dirname, mock_join, mock_open_file):
        """Testa o carregamento bem-sucedido de um arquivo de prompt"""
        # Arrange
        mock_dirname.return_value = '/fake/path'
        mock_join.return_value = '/fake/path/prompts/teste.md'
        tipo_analise = 'teste'
        
        # Act
        resultado = carregar_prompt(tipo_analise)
        
        # Assert
        assert resultado == "Prompt de teste"
        mock_open_file.assert_called_once_with('/fake/path/prompts/teste.md', 'r', encoding='utf-8')

    @patch('tools.revisor_geral.openai_client')
    @patch('tools.revisor_geral.carregar_prompt')
    def test_executar_analise_llm_erro_openai(self, mock_carregar_prompt, mock_openai_client):
        """Testa se RuntimeError é lançado quando há erro na chamada da API OpenAI"""
        # Arrange
        mock_carregar_prompt.return_value = "Prompt de sistema"
        mock_openai_client.chat.completions.create.side_effect = Exception("Erro de conexão")
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Erro ao comunicar com a OpenAI: Exception: Erro de conexão"):
            executar_analise_llm(
                tipo_analise='teste',
                codigo='codigo_teste',
                analise_extra='',
                model_name='gpt-3.5-turbo',
                max_token_out=1000
            )

    @patch('tools.revisor_geral.openai_client')
    @patch('tools.revisor_geral.carregar_prompt')
    def test_executar_analise_llm_prompt_extra(self, mock_carregar_prompt, mock_openai_client):
        """Testa se a mensagem de instrução extra é corretamente formatada e enviada"""
        # Arrange
        mock_carregar_prompt.return_value = "Prompt de sistema"
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Resposta da análise"
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        analise_extra = "Considere performance crítica"
        
        # Act
        resultado = executar_analise_llm(
            tipo_analise='teste',
            codigo='codigo_teste',
            analise_extra=analise_extra,
            model_name='gpt-3.5-turbo',
            max_token_out=1000
        )
        
        # Assert
        assert resultado == "Resposta da análise"
        
        # Verificar se as mensagens foram formatadas corretamente
        call_args = mock_openai_client.chat.completions.create.call_args
        mensagens = call_args[1]['messages']
        
        assert len(mensagens) == 3
        assert mensagens[0]['role'] == 'system'
        assert mensagens[0]['content'] == 'Prompt de sistema'
        assert mensagens[1]['role'] == 'user'
        assert mensagens[1]['content'] == 'codigo_teste'
        assert mensagens[2]['role'] == 'user'
        assert 'Considere performance crítica' in mensagens[2]['content']

    @patch('tools.revisor_geral.openai_client')
    @patch('tools.revisor_geral.carregar_prompt')
    def test_executar_analise_llm_sem_prompt_extra(self, mock_carregar_prompt, mock_openai_client):
        """Testa se a mensagem padrão é enviada quando analise_extra está vazia"""
        # Arrange
        mock_carregar_prompt.return_value = "Prompt de sistema"
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Resposta da análise"
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Act
        resultado = executar_analise_llm(
            tipo_analise='teste',
            codigo='codigo_teste',
            analise_extra='   ',  # String vazia/espaços
            model_name='gpt-3.5-turbo',
            max_token_out=1000
        )
        
        # Assert
        assert resultado == "Resposta da análise"
        
        # Verificar se a mensagem padrão foi enviada
        call_args = mock_openai_client.chat.completions.create.call_args
        mensagens = call_args[1]['messages']
        
        assert 'Nenhuma instrução extra fornecida pelo usuário.' in mensagens[2]['content']

    @patch('tools.revisor_geral.openai_client')
    @patch('tools.revisor_geral.carregar_prompt')
    def test_executar_analise_llm_parametros_corretos(self, mock_carregar_prompt, mock_openai_client):
        """Testa se os parâmetros são passados corretamente para a API OpenAI"""
        # Arrange
        mock_carregar_prompt.return_value = "Prompt de sistema"
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Resposta da análise"
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Act
        executar_analise_llm(
            tipo_analise='teste',
            codigo='codigo_teste',
            analise_extra='instrucao_extra',
            model_name='gpt-4',
            max_token_out=2000
        )
        
        # Assert
        mock_openai_client.chat.completions.create.assert_called_once_with(
            model='gpt-4',
            messages=[
                {'role': 'system', 'content': 'Prompt de sistema'},
                {'role': 'user', 'content': 'codigo_teste'},
                {'role': 'user', 'content': 'Instruções extras do usuário a serem consideradas na análise: instrucao_extra'}
            ],
            temperature=0.5,
            max_tokens=2000
        )

    @patch('builtins.print')
    @patch('tools.revisor_geral.openai_client')
    @patch('tools.revisor_geral.carregar_prompt')
    def test_executar_analise_llm_log_erro(self, mock_carregar_prompt, mock_openai_client, mock_print):
        """Testa se o erro é logado antes de ser relançado"""
        # Arrange
        mock_carregar_prompt.return_value = "Prompt de sistema"
        mock_openai_client.chat.completions.create.side_effect = ConnectionError("Falha de rede")
        
        # Act & Assert
        with pytest.raises(RuntimeError):
            executar_analise_llm(
                tipo_analise='teste',
                codigo='codigo_teste',
                analise_extra='',
                model_name='gpt-3.5-turbo',
                max_token_out=1000
            )
        
        # Verificar se o erro foi logado
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "ERRO: Falha na chamada à API da OpenAI para análise 'teste'" in call_args
        assert "ConnectionError: Falha de rede" in call_args