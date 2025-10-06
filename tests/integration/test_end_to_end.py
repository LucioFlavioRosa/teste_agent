import pytest
import os
from unittest.mock import patch, MagicMock, mock_open
from tools.github_reader import obter_arquivos_para_analise
from tools.revisor_geral import executar_analise_llm


class TestEndToEndIntegration:
    """Testes de integração ponta a ponta do sistema completo."""
    
    @pytest.fixture
    def mock_environment(self):
        """Fixture para mockar variáveis de ambiente."""
        with patch('tools.github_reader.userdata.get') as mock_github_token:
            with patch('tools.revisor_geral.userdata.get') as mock_openai_key:
                mock_github_token.return_value = 'fake_github_token'
                mock_openai_key.return_value = 'fake_openai_key'
                yield mock_github_token, mock_openai_key
    
    @pytest.fixture
    def mock_repository_files(self):
        """Fixture para mockar arquivos do repositório."""
        # Arquivo Python com configuração flexível
        mock_py_file = MagicMock()
        mock_py_file.path = 'app/config.py'
        mock_py_file.name = 'config.py'
        mock_py_file.type = 'file'
        mock_py_file.decoded_content = b'''
import os
from typing import Optional

class Config:
    """Configuração da aplicação usando variáveis de ambiente."""
    
    # Database configuration
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///default.db')
    DATABASE_POOL_SIZE: int = int(os.getenv('DATABASE_POOL_SIZE', '5'))
    
    # API configuration
    API_BASE_URL: str = os.getenv('API_BASE_URL', 'http://localhost:8000')
    API_TIMEOUT: int = int(os.getenv('API_TIMEOUT', '30'))
    
    # GitHub integration
    GITHUB_TOKEN: Optional[str] = os.getenv('GITHUB_TOKEN')
    GITHUB_API_URL: str = os.getenv('GITHUB_API_URL', 'https://api.github.com')
    
    # OpenAI configuration
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    @classmethod
    def validate_required_env_vars(cls):
        """Valida se todas as variáveis obrigatórias estão definidas."""
        required_vars = ['GITHUB_TOKEN', 'OPENAI_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Variáveis de ambiente obrigatórias não definidas: {missing_vars}")
'''
        
        # Arquivo Terraform com boas práticas
        mock_tf_file = MagicMock()
        mock_tf_file.path = 'infrastructure/main.tf'
        mock_tf_file.name = 'main.tf'
        mock_tf_file.type = 'file'
        mock_tf_file.decoded_content = b'''
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"
}

variable "database_url" {
  description = "Database connection URL"
  type        = string
  sensitive   = true
}

resource "aws_s3_bucket" "app_storage" {
  bucket = "app-storage-${var.environment}"
  
  versioning {
    enabled = true
  }
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_rds_instance" "app_database" {
  identifier = "app-db-${var.environment}"
  engine     = "postgresql"
  
  db_name  = "appdb"
  username = "admin"
  password = var.database_url
  
  encrypted = true
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  
  tags = {
    Environment = var.environment
    Project     = "code-analyzer"
  }
}
'''
        
        return [mock_py_file, mock_tf_file]
    
    def test_fluxo_completo_analise_python(self, mock_environment, mock_repository_files):
        """Testa o fluxo completo de análise de código Python."""
        mock_github_token, mock_openai_key = mock_environment
        
        # Mock do repositório GitHub
        with patch('tools.github_reader.Github') as mock_github_class:
            mock_github_instance = MagicMock()
            mock_repo = MagicMock()
            mock_github_instance.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github_instance
            
            # Retorna apenas o arquivo Python
            mock_repo.get_contents.return_value = [mock_repository_files[0]]
            
            # Mock da resposta da OpenAI
            mock_openai_response = MagicMock()
            mock_openai_response.choices[0].message.content = '''
# Análise de Código Python - Configuração

## Pontos Positivos
✅ **Configuração Flexível**: Uso adequado de `os.getenv()` para variáveis de ambiente
✅ **Valores Padrão**: Definição de valores padrão sensatos para desenvolvimento
✅ **Tipagem**: Uso de type hints para melhor documentação
✅ **Validação**: Método para validar variáveis obrigatórias

## Recomendações
- Considere usar bibliotecas como `pydantic-settings` para validação mais robusta
- Implemente logs para configurações carregadas (sem expor valores sensíveis)
'''
            
            prompt_content = "Analise a qualidade e segurança do código Python"
            
            with patch('builtins.open', mock_open(read_data=prompt_content)):
                with patch('tools.revisor_geral.openai_client.chat.completions.create') as mock_openai_create:
                    mock_openai_create.return_value = mock_openai_response
                    
                    # Executa o fluxo completo
                    arquivos = obter_arquivos_para_analise('user/test-repo', 'python')
                    
                    assert len(arquivos) == 1
                    assert 'app/config.py' in arquivos
                    assert 'os.getenv' in arquivos['app/config.py']
                    
                    # Executa análise LLM
                    resultado_analise = executar_analise_llm(
                        tipo_analise='python',
                        codigo=arquivos['app/config.py'],
                        analise_extra='Foque na configuração de variáveis de ambiente',
                        model_name='gpt-4',
                        max_token_out=2000
                    )
                    
                    assert 'Configuração Flexível' in resultado_analise
                    assert 'os.getenv()' in resultado_analise
    
    def test_fluxo_completo_analise_terraform(self, mock_environment, mock_repository_files):
        """Testa o fluxo completo de análise de código Terraform."""
        mock_github_token, mock_openai_key = mock_environment
        
        # Mock do repositório GitHub
        with patch('tools.github_reader.Github') as mock_github_class:
            mock_github_instance = MagicMock()
            mock_repo = MagicMock()
            mock_github_instance.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_github_instance
            
            # Retorna apenas o arquivo Terraform
            mock_repo.get_contents.return_value = [mock_repository_files[1]]
            
            # Mock da resposta da OpenAI
            mock_openai_response = MagicMock()
            mock_openai_response.choices[0].message.content = '''
# Análise de Infraestrutura Terraform

## Pontos Positivos
✅ **Variáveis Parametrizadas**: Uso de variáveis para environment e database_url
✅ **Segurança**: Configuração de criptografia no S3 e RDS
✅ **Backup**: Configuração adequada de backup para RDS
✅ **Versionamento**: S3 bucket com versionamento habilitado
✅ **Tags**: Uso de tags para organização de recursos

## Configuração para Testes
- Recursos configurados para aceitar variáveis de ambiente
- Possibilita criação de ambientes efêmeros para testes
'''
            
            prompt_content = "Analise a infraestrutura Terraform"
            
            with patch('builtins.open', mock_open(read_data=prompt_content)):
                with patch('tools.revisor_geral.openai_client.chat.completions.create') as mock_openai_create:
                    mock_openai_create.return_value = mock_openai_response
                    
                    # Executa o fluxo completo
                    arquivos = obter_arquivos_para_analise('user/test-repo', 'terraform')
                    
                    assert len(arquivos) == 1
                    assert 'infrastructure/main.tf' in arquivos
                    assert 'variable "environment"' in arquivos['infrastructure/main.tf']
                    
                    # Executa análise LLM
                    resultado_analise = executar_analise_llm(
                        tipo_analise='terraform',
                        codigo=arquivos['infrastructure/main.tf'],
                        analise_extra='Verifique a testabilidade da infraestrutura',
                        model_name='gpt-4',
                        max_token_out=2000
                    )
                    
                    assert 'Variáveis Parametrizadas' in resultado_analise
                    assert 'ambientes efêmeros' in resultado_analise
    
    def test_validacao_configuracao_ambiente_teste(self):
        """Testa se a configuração permite execução em ambiente de teste."""
        # Simula configuração para ambiente de teste
        test_env_vars = {
            'DATABASE_URL': 'postgresql://test:test@localhost:5432/testdb',
            'API_BASE_URL': 'http://localhost:8080',
            'GITHUB_API_URL': 'http://mock-github-api:3000',
            'OPENAI_API_KEY': 'test-key-for-integration-tests',
            'GITHUB_TOKEN': 'test-github-token'
        }
        
        with patch.dict(os.environ, test_env_vars):
            # Simula carregamento da configuração
            database_url = os.getenv('DATABASE_URL')
            api_base_url = os.getenv('API_BASE_URL')
            github_api_url = os.getenv('GITHUB_API_URL')
            
            # Verifica se as configurações de teste foram carregadas
            assert 'testdb' in database_url
            assert 'localhost:8080' in api_base_url
            assert 'mock-github-api' in github_api_url
            
            # Verifica se todas as variáveis obrigatórias estão presentes
            required_vars = ['GITHUB_TOKEN', 'OPENAI_API_KEY']
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            assert len(missing_vars) == 0, f"Variáveis obrigatórias ausentes: {missing_vars}"
