import pytest
import os
from unittest.mock import patch, mock_open, MagicMock
from tools.revisor_geral import carregar_prompt, executar_analise_llm


class TestRevisorGeral:
    """Testes unitários para o módulo revisor_geral.py"""

    @patch('tools.revisor_geral.userdata')
    def test_openai_api_key_ausente_lanca_erro(self, mock_userdata):
        """Testa se ValueError é lançado quando a chave da API está ausente"""
        mock_userdata.get.return_value = None
        
        with pytest.raises(ValueError) as exc_info:
            # Reimportar o módulo para forçar a execução da validação
            import importlib
            import tools.revisor_geral
            importlib.reload(tools.revisor_geral)
        
        assert "A chave da API da OpenAI não foi encontrada" in str(exc_info.value)
        mock_userdata.get.assert_called_once_with('OPENAI_API_KEY')

    @patch('builtins.open', mock_open(read_data="prompt content"))
    @patch('os.path.join')
    @patch('os.path.dirname')
    def test_carregar_prompt_sucesso(self, mock_dirname, mock_join):
        """Testa o carregamento bem-sucedido de um arquivo de prompt"""
        mock_dirname.return_value = '/fake/path'
        mock_join.return_value = '/fake/path/prompts/test.md'
        
        resultado = carregar_prompt('test')
        
        assert resultado == "prompt content"
        mock_join.assert_called_once_with('/fake/path', 'prompts', 'test.md')

    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    @patch('os.path.join')
    @patch('os.path.dirname')
    def test_carregar_prompt_arquivo_inexistente(self, mock_dirname, mock_join):
        """Testa se ValueError é lançado quando o arquivo de prompt não existe"""
        mock_dirname.return_value = '/fake/path'
        mock_join.return_value = '/fake/path/prompts/inexistente.md'
        
        with pytest.raises(ValueError) as exc_info:
            carregar_prompt('inexistente')
        
        assert "Arquivo de prompt para a análise 'inexistente' não encontrado" in str(exc_info.value)

    @patch('tools.revisor_geral.openai_client')
    @patch('tools.revisor_geral.carregar_prompt')
    def test_executar_analise_llm_sucesso(self, mock_carregar_prompt, mock_openai_client):
        """Testa execução bem-sucedida da análise LLM"""
        mock_carregar_prompt.return_value = "prompt sistema"
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "  resultado da análise  "
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        resultado = executar_analise_llm(
            tipo_analise='test',
            codigo='codigo teste',
            analise_extra='instrucoes extras',
            model_name='gpt-4',
            max_token_out=1000
        )
        
        assert resultado == "resultado da análise"
        mock_openai_client.chat.completions.create.assert_called_once()
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args[1]['model'] == 'gpt-4'
        assert call_args[1]['temperature'] == 0.5
        assert call_args[1]['max_tokens'] == 1000
        assert len(call_args[1]['messages']) == 3

    @patch('tools.revisor_geral.openai_client')
    @patch('tools.revisor_geral.carregar_prompt')
    def test_executar_analise_llm_falha_openai(self, mock_carregar_prompt, mock_openai_client):
        """Testa tratamento de falha na chamada da API OpenAI"""
        mock_carregar_prompt.return_value = "prompt sistema"
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        with pytest.raises(RuntimeError) as exc_info:
            executar_analise_llm(
                tipo_analise='test',
                codigo='codigo teste',
                analise_extra='',
                model_name='gpt-4',
                max_token_out=1000
            )
        
        assert "Erro ao comunicar com a OpenAI" in str(exc_info.value)
        assert "Exception: API Error" in str(exc_info.value)

    @patch('tools.revisor_geral.openai_client')
    @patch('tools.revisor_geral.carregar_prompt')
    def test_executar_analise_llm_sem_instrucoes_extras(self, mock_carregar_prompt, mock_openai_client):
        """Testa execução da análise LLM sem instruções extras"""
        mock_carregar_prompt.return_value = "prompt sistema"
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "resultado"
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        executar_analise_llm(
            tipo_analise='test',
            codigo='codigo teste',
            analise_extra='   ',  # String vazia/espaços
            model_name='gpt-4',
            max_token_out=1000
        )
        
        call_args = mock_openai_client.chat.completions.create.call_args
        mensagens = call_args[1]['messages']
        assert "Nenhuma instrução extra fornecida pelo usuário" in mensagens[2]['content']