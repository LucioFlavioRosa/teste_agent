import pytest
import unittest.mock as mock
from unittest.mock import MagicMock, patch, Mock
import time
from github import Github
from github.Auth import Token
import logging

# Importar as funções a serem testadas
from tools.github_reader import (
    conectar_ao_github,
    arquivo_esta_na_lista_de_extensoes,
    ler_conteudo_arquivo_com_retry,
    coletar_arquivos_e_diretorios,
    leitura_iterativa_com_paralelismo_e_retry,
    ler_arquivos_repositorio_github,
    obter_arquivos_para_analise,
    TIPO_EXTENSOES_MAPEAMENTO,
    MAX_RETRIES
)


class TestGithubReader:
    """Testes unitários para o módulo github_reader.py"""

    @patch('tools.github_reader.userdata')
    @patch('tools.github_reader.Github')
    def test_conectar_ao_github_sucesso(self, mock_github, mock_userdata):
        """Testa conexão bem-sucedida ao GitHub"""
        # Arrange
        mock_userdata.get.return_value = 'fake_token'
        mock_repo = MagicMock()
        mock_github_instance = MagicMock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance
        
        # Act
        resultado = conectar_ao_github('owner/repo')
        
        # Assert
        assert resultado == mock_repo
        mock_userdata.get.assert_called_once_with('github_token')
        mock_github.assert_called_once()
        mock_github_instance.get_repo.assert_called_once_with('owner/repo')

    @patch('tools.github_reader.userdata')
    def test_conectar_ao_github_token_ausente_levanta_erro(self, mock_userdata):
        """Testa que a ausência do token do GitHub resulta em ValueError"""
        # Arrange
        mock_userdata.get.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Token do GitHub não encontrado"):
            conectar_ao_github('owner/repo')
        
        mock_userdata.get.assert_called_once_with('github_token')

    @patch('tools.github_reader.userdata')
    @patch('tools.github_reader.Github')
    def test_conectar_ao_github_erro_github_api(self, mock_github, mock_userdata):
        """Testa tratamento de erro na API do GitHub"""
        # Arrange
        mock_userdata.get.return_value = 'fake_token'
        mock_github.side_effect = RuntimeError("API Error")
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="API Error"):
            conectar_ao_github('owner/repo')

    def test_arquivo_esta_na_lista_de_extensoes_extensao_match(self):
        """Testa arquivo que bate por extensão"""
        # Arrange
        mock_arquivo = MagicMock()
        mock_arquivo.path = 'src/main.py'
        mock_arquivo.name = 'main.py'
        extensoes = ['.py', '.js']
        
        # Act
        resultado = arquivo_esta_na_lista_de_extensoes(mock_arquivo, extensoes)
        
        # Assert
        assert resultado is True

    def test_arquivo_esta_na_lista_de_extensoes_nome_match(self):
        """Testa arquivo que bate por nome"""
        # Arrange
        mock_arquivo = MagicMock()
        mock_arquivo.path = 'docker/Dockerfile'
        mock_arquivo.name = 'Dockerfile'
        extensoes = ['Dockerfile', '.py']
        
        # Act
        resultado = arquivo_esta_na_lista_de_extensoes(mock_arquivo, extensoes)
        
        # Assert
        assert resultado is True

    def test_arquivo_esta_na_lista_de_extensoes_no_match(self):
        """Testa arquivo que não bate com nenhuma extensão"""
        # Arrange
        mock_arquivo = MagicMock()
        mock_arquivo.path = 'src/main.txt'
        mock_arquivo.name = 'main.txt'
        extensoes = ['.py', '.js']
        
        # Act
        resultado = arquivo_esta_na_lista_de_extensoes(mock_arquivo, extensoes)
        
        # Assert
        assert resultado is False

    def test_arquivo_esta_na_lista_de_extensoes_lista_none(self):
        """Testa comportamento quando lista de extensões é None"""
        # Arrange
        mock_arquivo = MagicMock()
        mock_arquivo.path = 'src/main.txt'
        
        # Act
        resultado = arquivo_esta_na_lista_de_extensoes(mock_arquivo, None)
        
        # Assert
        assert resultado is True

    def test_ler_conteudo_arquivo_com_retry_sucesso(self):
        """Testa leitura bem-sucedida de arquivo"""
        # Arrange
        mock_arquivo = MagicMock()
        mock_arquivo.decoded_content.decode.return_value = 'conteudo do arquivo'
        mock_arquivo.path = 'src/main.py'
        
        # Act
        resultado = ler_conteudo_arquivo_com_retry(mock_arquivo)
        
        # Assert
        assert resultado == 'conteudo do arquivo'
        mock_arquivo.decoded_content.decode.assert_called_once_with('utf-8')

    def test_ler_conteudo_arquivo_com_retry_attribute_error(self):
        """Testa tratamento de AttributeError"""
        # Arrange
        mock_arquivo = MagicMock()
        mock_arquivo.decoded_content = None
        mock_arquivo.path = 'src/main.py'
        
        # Act
        resultado = ler_conteudo_arquivo_com_retry(mock_arquivo)
        
        # Assert
        assert resultado is None

    @patch('tools.github_reader.time.sleep')
    def test_ler_conteudo_arquivo_com_retry_falha_e_retry(self, mock_sleep):
        """Testa mecanismo de retry em caso de falha temporária"""
        # Arrange
        mock_arquivo = MagicMock()
        mock_arquivo.path = 'src/main.py'
        mock_arquivo.decoded_content.decode.side_effect = [
            Exception("Erro temporário"),
            Exception("Erro temporário 2"),
            Exception("Erro final")
        ]
        
        # Act
        resultado = ler_conteudo_arquivo_com_retry(mock_arquivo)
        
        # Assert
        assert resultado is None
        assert mock_arquivo.decoded_content.decode.call_count == MAX_RETRIES
        assert mock_sleep.call_count == MAX_RETRIES - 1

    def test_coletar_arquivos_e_diretorios(self):
        """Testa separação de arquivos e diretórios"""
        # Arrange
        mock_arquivo1 = MagicMock()
        mock_arquivo1.type = "file"
        mock_arquivo1.path = 'src/main.py'
        mock_arquivo1.name = 'main.py'
        
        mock_arquivo2 = MagicMock()
        mock_arquivo2.type = "file"
        mock_arquivo2.path = 'src/test.txt'
        mock_arquivo2.name = 'test.txt'
        
        mock_dir = MagicMock()
        mock_dir.type = "dir"
        mock_dir.path = 'src/utils'
        
        conteudos = [mock_arquivo1, mock_dir, mock_arquivo2]
        extensoes = ['.py']
        
        # Act
        arquivos, diretorios = coletar_arquivos_e_diretorios(conteudos, extensoes)
        
        # Assert
        assert len(arquivos) == 1
        assert arquivos[0] == mock_arquivo1
        assert diretorios == ['src/utils']

    @patch('tools.github_reader.concurrent.futures.ThreadPoolExecutor')
    def test_leitura_iterativa_com_paralelismo_e_retry_limite_profundidade(self, mock_executor):
        """Testa que max_depth limita corretamente a recursão"""
        # Arrange
        mock_repo = MagicMock()
        mock_arquivo = MagicMock()
        mock_arquivo.type = "file"
        mock_arquivo.path = 'root.py'
        mock_arquivo.name = 'root.py'
        
        mock_dir = MagicMock()
        mock_dir.type = "dir"
        mock_dir.path = 'subdir'
        
        # Primeiro nível - retorna arquivo e diretório
        mock_repo.get_contents.side_effect = [
            [mock_arquivo, mock_dir],  # Conteúdo da raiz
            []  # Conteúdo do subdir (não deve ser chamado devido ao max_depth)
        ]
        
        # Mock do executor
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        mock_executor_instance.submit.return_value = MagicMock()
        mock_executor_instance.submit.return_value.result.return_value = 'conteudo'
        
        # Act
        resultado = leitura_iterativa_com_paralelismo_e_retry(
            mock_repo, ['.py'], caminho_inicial="", max_depth=0
        )
        
        # Assert
        assert 'root.py' in resultado
        # Verifica que get_contents foi chamado apenas uma vez (para a raiz)
        assert mock_repo.get_contents.call_count == 1

    @patch('tools.github_reader.conectar_ao_github')
    @patch('tools.github_reader.leitura_iterativa_com_paralelismo_e_retry')
    def test_ler_arquivos_repositorio_github_sucesso(self, mock_leitura, mock_conectar):
        """Testa leitura bem-sucedida de arquivos do repositório"""
        # Arrange
        mock_repo = MagicMock()
        mock_conectar.return_value = mock_repo
        mock_leitura.return_value = {'src/main.py': 'conteudo'}
        
        # Act
        resultado = ler_arquivos_repositorio_github('owner/repo', 'python')
        
        # Assert
        assert resultado == {'src/main.py': 'conteudo'}
        mock_conectar.assert_called_once_with(repositorio_nome='owner/repo')
        mock_leitura.assert_called_once_with(
            mock_repo, ['.py'], max_workers=4, max_depth=None
        )

    @patch('tools.github_reader.conectar_ao_github')
    def test_ler_arquivos_repositorio_github_erro_conexao(self, mock_conectar):
        """Testa tratamento de erro na conexão"""
        # Arrange
        mock_conectar.side_effect = ValueError("Erro de conexão")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Erro de conexão"):
            ler_arquivos_repositorio_github('owner/repo', 'python')

    @patch('tools.github_reader.ler_arquivos_repositorio_github')
    def test_obter_arquivos_para_analise(self, mock_ler_arquivos):
        """Testa função wrapper obter_arquivos_para_analise"""
        # Arrange
        mock_ler_arquivos.return_value = {'src/main.py': 'conteudo'}
        
        # Act
        resultado = obter_arquivos_para_analise('owner/repo', 'python', max_workers=2, max_depth=5)
        
        # Assert
        assert resultado == {'src/main.py': 'conteudo'}
        mock_ler_arquivos.assert_called_once_with('owner/repo', 'python', max_workers=2, max_depth=5)

    def test_tipo_extensoes_mapeamento_contem_tipos_esperados(self):
        """Testa se o mapeamento de extensões contém os tipos esperados"""
        # Assert
        assert 'python' in TIPO_EXTENSOES_MAPEAMENTO
        assert 'terraform' in TIPO_EXTENSOES_MAPEAMENTO
        assert 'cloudformation' in TIPO_EXTENSOES_MAPEAMENTO
        assert 'ansible' in TIPO_EXTENSOES_MAPEAMENTO
        assert 'docker' in TIPO_EXTENSOES_MAPEAMENTO
        
        assert TIPO_EXTENSOES_MAPEAMENTO['python'] == ['.py']
        assert TIPO_EXTENSOES_MAPEAMENTO['terraform'] == ['.tf', '.tfvars']
        assert TIPO_EXTENSOES_MAPEAMENTO['docker'] == ['Dockerfile']