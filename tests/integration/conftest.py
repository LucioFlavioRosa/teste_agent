import pytest
import os
from unittest.mock import patch


@pytest.fixture(scope="session")
def test_environment():
    """Fixture de sessão para configurar ambiente de teste."""
    test_env_vars = {
        'DATABASE_URL': 'sqlite:///test.db',
        'API_BASE_URL': 'http://localhost:8080',
        'API_TIMEOUT': '10',
        'GITHUB_API_URL': 'http://mock-github:3000',
        'GITHUB_TOKEN': 'test-github-token-12345',
        'OPENAI_API_KEY': 'test-openai-key-67890',
        'OPENAI_MODEL': 'gpt-3.5-turbo',
        'DATABASE_POOL_SIZE': '2',
        'LOG_LEVEL': 'DEBUG'
    }
    
    with patch.dict(os.environ, test_env_vars):
        yield test_env_vars


@pytest.fixture
def mock_github_api():
    """Fixture para mockar chamadas à API do GitHub."""
    with patch('tools.github_reader.Github') as mock_github:
        mock_instance = mock_github.return_value
        mock_repo = mock_instance.get_repo.return_value
        mock_repo.name = 'test-repository'
        mock_repo.full_name = 'user/test-repository'
        yield mock_github


@pytest.fixture
def mock_openai_api():
    """Fixture para mockar chamadas à API da OpenAI."""
    with patch('tools.revisor_geral.openai_client.chat.completions.create') as mock_create:
        mock_response = type('MockResponse', (), {})()
        mock_choice = type('MockChoice', (), {})()
        mock_message = type('MockMessage', (), {})()
        mock_message.content = "Análise de teste concluída com sucesso."
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_create.return_value = mock_response
        yield mock_create


@pytest.fixture
def sample_python_code():
    """Fixture com código Python de exemplo para testes."""
    return '''
import os
from typing import Optional

class DatabaseConfig:
    """Configuração de banco de dados com variáveis de ambiente."""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '5432'))
        self.database = os.getenv('DB_NAME', 'myapp')
        self.username = os.getenv('DB_USER', 'user')
        self.password = os.getenv('DB_PASSWORD', 'password')
        self.pool_size = int(os.getenv('DB_POOL_SIZE', '5'))
    
    def get_connection_string(self) -> str:
        """Retorna string de conexão com o banco."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def validate_config(self) -> bool:
        """Valida se a configuração está completa."""
        required_fields = [self.host, self.database, self.username, self.password]
        return all(field for field in required_fields)
'''


@pytest.fixture
def sample_terraform_code():
    """Fixture com código Terraform de exemplo para testes."""
    return '''
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "database_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

resource "aws_rds_instance" "main" {
  identifier = "app-db-${var.environment}"
  
  engine         = "postgresql"
  engine_version = "13.7"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_encrypted     = true
  
  db_name  = "appdb"
  username = "dbadmin"
  password = var.database_password
  
  backup_retention_period = var.environment == "prod" ? 30 : 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = var.environment != "prod"
  
  tags = {
    Name        = "app-database-${var.environment}"
    Environment = var.environment
    Terraform   = "true"
  }
}

output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_rds_instance.main.endpoint
  sensitive   = false
}
'''
