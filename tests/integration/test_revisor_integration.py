import pytest
import os
from unittest.mock import patch, MagicMock, mock_open
from tools.revisor_geral import (
    carregar_prompt,
    executar_analise_llm
)


class TestRevisorIntegration:
    """Testes de integração para o módulo Revisor Geral."""
    
    @pytest.fixture
    def mock_openai_key(self):
        """Fixture para mockar a chave da API OpenAI."""
        with patch('tools.revisor_geral.userdata.get') as mock_userdata:
            mock_userdata.return_value = 'fake_openai_key_for_tests'
            yield mock_userdata
    
    @pytest.fixture
    def mock_openai_response(self):
        """Fixture para mockar resposta da OpenAI."""
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Análise de segurança concluída. Nenhuma vulnerabilidade crítica encontrada."
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        return mock_response
    
    def test_carregar_prompt_sucesso(self):
        """Testa carregamento bem-sucedido de prompt."""
        prompt_content = "# Prompt de Análise de Segurança\nAnalise o código fornecido..."
        
        with patch('builtins.open', mock_open(read_data=prompt_content)):
            with patch('os.path.join', return_value='/fake/path/seguranca.md'):
                resultado = carregar_prompt('seguranca')
                
                assert resultado == prompt_content
    
    def test_carregar_prompt_arquivo_nao_encontrado(self):
        """Testa falha no carregamento quando arquivo de prompt não existe."""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            with pytest.raises(ValueError, match="Arquivo de prompt para a análise 'inexistente' não encontrado"):
                carregar_prompt('inexistente')
    
    def test_executar_analise_llm_sucesso(self, mock_openai_key, mock_openai_response):
        """Testa execução bem-sucedida de análise LLM."""
        prompt_content = "Analise o código de segurança"
        codigo_teste = "import hashlib\npassword = 'test123'"
        
        with patch('builtins.open', mock_open(read_data=prompt_content)):
            with patch('os.path.join', return_value='/fake/path/seguranca.md'):
                with patch('tools.revisor_geral.openai_client.chat.completions.create') as mock_create:
                    mock_create.return_value = mock_openai_response
                    
                    resultado = executar_analise_llm(
                        tipo_analise='seguranca',
                        codigo=codigo_teste,
                        analise_extra='Foque em vulnerabilidades de senha',
                        model_name='gpt-4',
                        max_token_out=1000
                    )
                    
                    assert "Análise de segurança concluída" in resultado
                    mock_create.assert_called_once()
    
    def test_executar_analise_llm_erro_api(self, mock_openai_key):
        """Testa tratamento de erro na API da OpenAI."""
        prompt_content = "Analise o código"
        codigo_teste = "print('hello')"
        
        with patch('builtins.open', mock_open(read_data=prompt_content)):
            with patch('os.path.join', return_value='/fake/path/python.md'):
                with patch('tools.revisor_geral.openai_client.chat.completions.create') as mock_create:
                    mock_create.side_effect = Exception("API Error")
                    
                    with pytest.raises(RuntimeError, match="Erro ao comunicar com a OpenAI"):
                        executar_analise_llm(
                            tipo_analise='python',
                            codigo=codigo_teste,
                            analise_extra='',
                            model_name='gpt-4',
                            max_token_out=1000
                        )
    
    def test_integração_completa_analise_terraform(self, mock_openai_key, mock_openai_response):
        """Testa fluxo completo de análise Terraform."""
        prompt_terraform = "# Análise Terraform\nVerifique boas práticas de IaC"
        codigo_terraform = '''
resource "aws_s3_bucket" "example" {
  bucket = "my-bucket"
  
  versioning {
    enabled = true
  }
}
'''
        
        mock_openai_response.choices[0].message.content = "Análise Terraform: Bucket S3 configurado corretamente com versionamento."
        
        with patch('builtins.open', mock_open(read_data=prompt_terraform)):
            with patch('os.path.join', return_value='/fake/path/terraform.md'):
                with patch('tools.revisor_geral.openai_client.chat.completions.create') as mock_create:
                    mock_create.return_value = mock_openai_response
                    
                    resultado = executar_analise_llm(
                        tipo_analise='terraform',
                        codigo=codigo_terraform,
                        analise_extra='Verifique configurações de segurança do S3',
                        model_name='gpt-4',
                        max_token_out=2000
                    )
                    
                    assert "Bucket S3 configurado corretamente" in resultado
                    
                    # Verifica se a chamada foi feita com os parâmetros corretos
                    call_args = mock_create.call_args
                    assert call_args[1]['model'] == 'gpt-4'
                    assert call_args[1]['max_tokens'] == 2000
                    assert len(call_args[1]['messages']) == 3  # system + user + extra
    
    def test_integração_analise_sem_instrucoes_extras(self, mock_openai_key, mock_openai_response):
        """Testa análise sem instruções extras do usuário."""
        prompt_content = "Analise o código Python"
        codigo_python = "def hello():\n    return 'Hello World'"
        
        with patch('builtins.open', mock_open(read_data=prompt_content)):
            with patch('os.path.join', return_value='/fake/path/python.md'):
                with patch('tools.revisor_geral.openai_client.chat.completions.create') as mock_create:
                    mock_create.return_value = mock_openai_response
                    
                    resultado = executar_analise_llm(
                        tipo_analise='python',
                        codigo=codigo_python,
                        analise_extra='',  # Sem instruções extras
                        model_name='gpt-3.5-turbo',
                        max_token_out=500
                    )
                    
                    # Verifica se a mensagem sobre "nenhuma instrução extra" foi incluída
                    call_args = mock_create.call_args
                    messages = call_args[1]['messages']
                    assert any('Nenhuma instrução extra fornecida' in msg['content'] for msg in messages)
