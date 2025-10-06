import pytest
import os
from unittest.mock import patch, MagicMock
from tools.github_reader import (
    conectar_ao_github,
    ler_arquivos_repositorio_github,
    obter_arquivos_para_analise
)


class TestGitHubIntegration:
    """Testes de integração para o módulo GitHub Reader."""
    
    @pytest.fixture
    def mock_github_token(self):
        """Fixture para mockar o token do GitHub."""
        with patch('tools.github_reader.userdata.get') as mock_userdata:
            mock_userdata.return_value = 'fake_github_token_for_tests'
            yield mock_userdata
    
    @pytest.fixture
    def mock_github_repo(self):
        """Fixture para mockar um repositório GitHub."""
        mock_repo = MagicMock()
        mock_repo.name = 'test-repo'
        mock_repo.full_name = 'user/test-repo'
        return mock_repo
    
    @pytest.fixture
    def mock_file_content(self):
        """Fixture para mockar conteúdo de arquivo."""
        mock_file = MagicMock()
        mock_file.path = 'test_file.py'
        mock_file.name = 'test_file.py'
        mock_file.type = 'file'
        mock_file.decoded_content = b'# Test Python file\nprint("Hello World")'
        return mock_file
    
    def test_conectar_ao_github_sucesso(self, mock_github_token, mock_github_repo):
        """Testa conexão bem-sucedida com o GitHub."""
        with patch('tools.github_reader.Github') as mock_github_class:
            mock_github_instance = MagicMock()
            mock_github_instance.get_repo.return_value = mock_github_repo
            mock_github_class.return_value = mock_github_instance
            
            resultado = conectar_ao_github('user/test-repo')
            
            assert resultado == mock_github_repo
            mock_github_token.assert_called_once_with('github_token')
            mock_github_instance.get_repo.assert_called_once_with('user/test-repo')
    
    def test_conectar_ao_github_sem_token(self):
        """Testa falha na conexão quando token não está disponível."""
        with patch('tools.github_reader.userdata.get', return_value=None):
            with pytest.raises(ValueError, match="Token do GitHub não encontrado"):
                conectar_ao_github('user/test-repo')
    
    def test_ler_arquivos_repositorio_python(self, mock_github_token, mock_github_repo, mock_file_content):
        """Testa leitura de arquivos Python do repositório."""
        with patch('tools.github_reader.Github') as mock_github_class:
            mock_github_instance = MagicMock()
            mock_github_instance.get_repo.return_value = mock_github_repo
            mock_github_class.return_value = mock_github_instance
            
            mock_github_repo.get_contents.return_value = [mock_file_content]
            
            resultado = ler_arquivos_repositorio_github('user/test-repo', 'python')
            
            assert 'test_file.py' in resultado
            assert '# Test Python file' in resultado['test_file.py']
    
    def test_obter_arquivos_para_analise_terraform(self, mock_github_token, mock_github_repo):
        """Testa obtenção de arquivos para análise Terraform."""
        mock_tf_file = MagicMock()
        mock_tf_file.path = 'main.tf'
        mock_tf_file.name = 'main.tf'
        mock_tf_file.type = 'file'
        mock_tf_file.decoded_content = b'resource "aws_instance" "example" {}'
        
        with patch('tools.github_reader.Github') as mock_github_class:
            mock_github_instance = MagicMock()
            mock_github_instance.get_repo.return_value = mock_github_repo
            mock_github_class.return_value = mock_github_instance
            
            mock_github_repo.get_contents.return_value = [mock_tf_file]
            
            resultado = obter_arquivos_para_analise('user/test-repo', 'terraform')
            
            assert 'main.tf' in resultado
            assert 'aws_instance' in resultado['main.tf']
    
    def test_integração_completa_fluxo_analise(self, mock_github_token, mock_github_repo):
        """Testa o fluxo completo de análise de código."""
        # Simula múltiplos arquivos de diferentes tipos
        mock_py_file = MagicMock()
        mock_py_file.path = 'app.py'
        mock_py_file.name = 'app.py'
        mock_py_file.type = 'file'
        mock_py_file.decoded_content = b'import os\nprint("Application started")'
        
        mock_config_file = MagicMock()
        mock_config_file.path = 'config.py'
        mock_config_file.name = 'config.py'
        mock_config_file.type = 'file'
        mock_config_file.decoded_content = b'DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///default.db")'
        
        with patch('tools.github_reader.Github') as mock_github_class:
            mock_github_instance = MagicMock()
            mock_github_instance.get_repo.return_value = mock_github_repo
            mock_github_class.return_value = mock_github_instance
            
            mock_github_repo.get_contents.return_value = [mock_py_file, mock_config_file]
            
            resultado = obter_arquivos_para_analise('user/test-repo', 'python')
            
            # Verifica se ambos os arquivos foram processados
            assert len(resultado) == 2
            assert 'app.py' in resultado
            assert 'config.py' in resultado
            
            # Verifica conteúdo específico
            assert 'import os' in resultado['app.py']
            assert 'DATABASE_URL' in resultado['config.py']
            assert 'os.getenv' in resultado['config.py']  # Verifica uso de variáveis de ambiente
