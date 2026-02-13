import pytest
import unittest.mock as mock
from unittest.mock import MagicMock, patch, mock_open
import os

# Importar as funções a serem testadas
from tools.revisor_geral import (
    carregar_prompt,
    executar_analise_llm
)


class TestRevisorGeral:
    """Testes unitários para o módulo revisor_geral.py"""

    @patch('builtins.open', new_callable=mock_open, read_data='Prompt de teste')
    @patch('os.path.join')
    @patch('os.path.dirname')
    def test_carregar_prompt_sucesso(self, mock_dirname, mock_join, mock_file):
        """Testa carregamento bem-sucedido de prompt"""
        # Arrange
        mock_dirname.return_value = '/tools'
        mock_join.return_value = '/tools/prompts/python.md'
        
        # Act
        resultado = carregar_prompt('python')
        
        # Assert
        assert resultado == 'Prompt de teste'
        mock_dirname.assert_called_once()
        mock_join.assert_called_once_with('/tools', 'prompts', 'python.md')
        mock_file.assert_called_once_with('/tools/prompts/python.md', 'r', encoding='utf-8')

    @patch('builtins.open')
    @patch('os.path.join')
    @patch('os.path.dirname')
    def test_carregar_prompt_arquivo_inexistente(self, mock_dirname, mock_join, mock_open_func):
        """Testa que a função lança ValueError ao tentar carregar arquivo inexistente"""
        # Arrange
        mock_dirname.return_value = '/tools'
        mock_join.return_value = '/tools/prompts/inexistente.md'
        mock_open_func.side_effect = FileNotFoundError("Arquivo não encontrado")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Arquivo de prompt para a análise 'inexistente' não encontrado"):
            carregar_prompt('inexistente')
        
        mock_open_func.assert_called_once_with('/tools/prompts/inexistente.md', 'r', encoding='utf-8')

    @patch('tools.revisor_geral.carregar_prompt')
    @patch('tools.revisor_geral.openai_client')
    def test_executar_analise_llm_sucesso(self, mock_client, mock_carregar_prompt):
        """Testa execução bem-sucedida de análise LLM"""
        # Arrange
        mock_carregar_prompt.return_value = 'Prompt do sistema'
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '  Resultado da análise  '
        mock_client.chat.completions.create.return_value = mock_response
        
        codigo = 'def test(): pass'
        analise_extra = 'Verificar performance'
        
        # Act
        resultado = executar_analise_llm(
            tipo_analise='python',
            codigo=codigo,
            analise_extra=analise_extra,
            model_name='gpt-4',
            max_token_out=1000
        )
        
        # Assert
        assert resultado == 'Resultado da análise'
        mock_carregar_prompt.assert_called_once_with('python')
        
        # Verificar chamada à API da OpenAI
        expected_messages = [
            {"role": "system", "content": "Prompt do sistema"},
            {'role': 'user', 'content': codigo},
            {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}'}
        ]
        
        mock_client.chat.completions.create.assert_called_once_with(
            model='gpt-4',
            messages=expected_messages,
            temperature=0.5,
            max_tokens=1000
        )

    @patch('tools.revisor_geral.carregar_prompt')
    @patch('tools.revisor_geral.openai_client')
    def test_executar_analise_llm_sem_analise_extra(self, mock_client, mock_carregar_prompt):
        """Testa execução de análise LLM sem instruções extras"""
        # Arrange
        mock_carregar_prompt.return_value = 'Prompt do sistema'
        mock_response = MagicMock()
        mock_response.choices[0].message.content = 'Resultado da análise'
        mock_client.chat.completions.create.return_value = mock_response
        
        codigo = 'def test(): pass'
        analise_extra = '   '  # String vazia/espaços
        
        # Act
        resultado = executar_analise_llm(
            tipo_analise='python',
            codigo=codigo,
            analise_extra=analise_extra,
            model_name='gpt-3.5-turbo',
            max_token_out=500
        )
        
        # Assert
        assert resultado == 'Resultado da análise'
        
        # Verificar que a mensagem padrão foi usada para análise extra
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        assert messages[2]['content'] == 'Nenhuma instrução extra fornecida pelo usuário.'

    @patch('tools.revisor_geral.carregar_prompt')
    @patch('tools.revisor_geral.openai_client')
    def test_executar_analise_llm_erro_openai(self, mock_client, mock_carregar_prompt):
        """Testa tratamento de erro na chamada à API da OpenAI"""
        # Arrange
        mock_carregar_prompt.return_value = 'Prompt do sistema'
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Erro ao comunicar com a OpenAI: Exception: API Error"):
            executar_analise_llm(
                tipo_analise='python',
                codigo='def test(): pass',
                analise_extra='',
                model_name='gpt-4',
                max_token_out=1000
            )

    @patch('tools.revisor_geral.carregar_prompt')
    @patch('tools.revisor_geral.openai_client')
    def test_executar_analise_llm_erro_carregar_prompt(self, mock_client, mock_carregar_prompt):
        """Testa tratamento de erro ao carregar prompt"""
        # Arrange
        mock_carregar_prompt.side_effect = ValueError("Prompt não encontrado")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Prompt não encontrado"):
            executar_analise_llm(
                tipo_analise='inexistente',
                codigo='def test(): pass',
                analise_extra='',
                model_name='gpt-4',
                max_token_out=1000
            )
        
        # Verificar que a API da OpenAI não foi chamada
        mock_client.chat.completions.create.assert_not_called()

    @patch('tools.revisor_geral.userdata')
    def test_openai_api_key_ausente(self, mock_userdata):
        """Testa comportamento quando a chave da API da OpenAI está ausente"""
        # Arrange
        mock_userdata.get.return_value = None
        
        # Act & Assert
        # Este teste verifica se o módulo levanta erro na importação
        # quando a chave da API não está disponível
        with pytest.raises(ValueError, match="A chave da API da OpenAI não foi encontrada"):
            # Simular reimportação do módulo
            import importlib
            import sys
            if 'tools.revisor_geral' in sys.modules:
                del sys.modules['tools.revisor_geral']
            
            # Patch userdata antes da importação
            with patch('tools.revisor_geral.userdata', mock_userdata):
                import tools.revisor_geral

    def test_parametros_openai_client_corretos(self):
        """Testa se os parâmetros da chamada à OpenAI estão corretos"""
        # Este teste verifica se os parâmetros padrão estão sendo usados corretamente
        with patch('tools.revisor_geral.carregar_prompt') as mock_carregar_prompt, \
             patch('tools.revisor_geral.openai_client') as mock_client:
            
            # Arrange
            mock_carregar_prompt.return_value = 'Prompt teste'
            mock_response = MagicMock()
            mock_response.choices[0].message.content = 'Resposta teste'
            mock_client.chat.completions.create.return_value = mock_response
            
            # Act
            executar_analise_llm(
                tipo_analise='test',
                codigo='codigo teste',
                analise_extra='extra teste',
                model_name='gpt-4-turbo',
                max_token_out=2000
            )
            
            # Assert
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]['model'] == 'gpt-4-turbo'
            assert call_args[1]['temperature'] == 0.5
            assert call_args[1]['max_tokens'] == 2000
            assert len(call_args[1]['messages']) == 3
            assert call_args[1]['messages'][0]['role'] == 'system'
            assert call_args[1]['messages'][1]['role'] == 'user'
            assert call_args[1]['messages'][2]['role'] == 'user'