import pytest
import unittest.mock as mock
from unittest.mock import MagicMock, patch, PropertyMock
import concurrent.futures
import time
from typing import List, Optional

# Importar o módulo a ser testado
from tools.github_reader import (
    conectar_ao_github,
    arquivo_esta_na_lista_de_extensoes,
    ler_conteudo_arquivo_com_retry,
    coletar_arquivos_e_diretorios,
    leitura_iterativa_com_paralelismo_e_retry,
    ler_arquivos_repositorio_github,
    obter_arquivos_para_analise,
    TIPO_EXTENSOES_MAPEAMENTO,
    MAX_RETRIES,
    RETRY_DELAY
)


class TestConectarAoGithub:
    """Testes para a função conectar_ao_github"""
    
    @patch('tools.github_reader.userdata')
    @patch('tools.github_reader.Github')
    @patch('tools.github_reader.Token')
    def test_conectar_ao_github_sucesso(self, mock_token, mock_github, mock_userdata):
        """Teste de conexão bem-sucedida ao GitHub"""
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
        mock_token.assert_called_once_with('fake_token')
        mock_github.assert_called_once()
        mock_github_instance.get_repo.assert_called_once_with('owner/repo')
    
    @patch('tools.github_reader.userdata')
    def test_conectar_ao_github_token_ausente(self, mock_userdata):
        """Teste para garantir que a ausência do token resulta em exceção apropriada"""
        # Arrange
        mock_userdata.get.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Token do GitHub não encontrado"):
            conectar_ao_github('owner/repo')
        
        mock_userdata.get.assert_called_once_with('github_token')
    
    @patch('tools.github_reader.userdata')
    @patch('tools.github_reader.Github')
    @patch('tools.github_reader.Token')
    def test_conectar_ao_github_token_invalido(self, mock_token, mock_github, mock_userdata):
        """Teste para simular token inválido e garantir tratamento correto da exceção"""
        # Arrange
        mock_userdata.get.return_value = 'invalid_token'
        mock_github.side_effect = RuntimeError("Bad credentials")
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Bad credentials"):
            conectar_ao_github('owner/repo')
        
        mock_userdata.get.assert_called_once_with('github_token')
        mock_token.assert_called_once_with('invalid_token')


class TestArquivoEstaNaListaDeExtensoes:
    """Testes para a função arquivo_esta_na_lista_de_extensoes"""
    
    def test_arquivo_esta_na_lista_de_extensoes_varios_casos(self):
        """Teste cobrindo vários casos de extensões e nomes de arquivo"""
        # Arrange
        mock_arquivo_py = MagicMock()
        mock_arquivo_py.path = 'src/main.py'
        mock_arquivo_py.name = 'main.py'
        
        mock_arquivo_dockerfile = MagicMock()
        mock_arquivo_dockerfile.path = 'docker/Dockerfile'
        mock_arquivo_dockerfile.name = 'Dockerfile'
        
        mock_arquivo_txt = MagicMock()
        mock_arquivo_txt.path = 'docs/readme.txt'
        mock_arquivo_txt.name = 'readme.txt'
        
        extensoes_python = ['.py']
        extensoes_docker = ['Dockerfile']
        extensoes_mistas = ['.py', '.js', 'Dockerfile']
        
        # Act & Assert
        assert arquivo_esta_na_lista_de_extensoes(mock_arquivo_py, extensoes_python) == True
        assert arquivo_esta_na_lista_de_extensoes(mock_arquivo_dockerfile, extensoes_docker) == True
        assert arquivo_esta_na_lista_de_extensoes(mock_arquivo_py, extensoes_mistas) == True
        assert arquivo_esta_na_lista_de_extensoes(mock_arquivo_dockerfile, extensoes_mistas) == True
        assert arquivo_esta_na_lista_de_extensoes(mock_arquivo_txt, extensoes_python) == False
        assert arquivo_esta_na_lista_de_extensoes(mock_arquivo_txt, extensoes_docker) == False
    
    def test_arquivo_esta_na_lista_de_extensoes_lista_none(self):
        """Teste quando a lista de extensões é None (deve retornar True)"""
        # Arrange
        mock_arquivo = MagicMock()
        mock_arquivo.path = 'qualquer/arquivo.xyz'
        
        # Act & Assert
        assert arquivo_esta_na_lista_de_extensoes(mock_arquivo, None) == True


class TestLerConteudoArquivoComRetry:
    """Testes para a função ler_conteudo_arquivo_com_retry"""
    
    def test_ler_conteudo_arquivo_com_retry_sucesso(self):
        """Teste de leitura bem-sucedida na primeira tentativa"""
        # Arrange
        mock_arquivo = MagicMock()
        mock_arquivo.decoded_content.decode.return_value = 'conteudo do arquivo'
        mock_arquivo.path = 'test/file.py'
        
        # Act
        resultado = ler_conteudo_arquivo_com_retry(mock_arquivo)
        
        # Assert
        assert resultado == 'conteudo do arquivo'
        mock_arquivo.decoded_content.decode.assert_called_once_with('utf-8')
    
    def test_ler_conteudo_arquivo_com_retry_attribute_error(self):
        """Teste para arquivo sem conteúdo decodificável"""
        # Arrange
        mock_arquivo = MagicMock()
        mock_arquivo.decoded_content = None
        mock_arquivo.path = 'test/binary_file'
        
        # Act
        resultado = ler_conteudo_arquivo_com_retry(mock_arquivo)
        
        # Assert
        assert resultado is None
    
    @patch('tools.github_reader.time.sleep')
    def test_ler_conteudo_arquivo_com_retry_falha_e_retry(self, mock_sleep):
        """Teste para validar mecanismo de retry após falhas"""
        # Arrange
        mock_arquivo = MagicMock()
        mock_arquivo.decoded_content.decode.side_effect = [
            Exception("Erro temporário"),
            Exception("Erro temporário 2"),
            Exception("Erro final")
        ]
        mock_arquivo.path = 'test/problematic_file.py'
        
        # Act
        resultado = ler_conteudo_arquivo_com_retry(mock_arquivo)
        
        # Assert
        assert resultado is None
        assert mock_arquivo.decoded_content.decode.call_count == MAX_RETRIES
        assert mock_sleep.call_count == MAX_RETRIES - 1
        mock_sleep.assert_called_with(RETRY_DELAY)
    
    @patch('tools.github_reader.time.sleep')
    def test_ler_conteudo_arquivo_com_retry_sucesso_na_segunda_tentativa(self, mock_sleep):
        """Teste para sucesso após uma falha inicial"""
        # Arrange
        mock_arquivo = MagicMock()
        mock_arquivo.decoded_content.decode.side_effect = [
            Exception("Erro temporário"),
            'conteudo recuperado'
        ]
        mock_arquivo.path = 'test/recovered_file.py'
        
        # Act
        resultado = ler_conteudo_arquivo_com_retry(mock_arquivo)
        
        # Assert
        assert resultado == 'conteudo recuperado'
        assert mock_arquivo.decoded_content.decode.call_count == 2
        mock_sleep.assert_called_once_with(RETRY_DELAY)


class TestColetarArquivosEDiretorios:
    """Testes para a função coletar_arquivos_e_diretorios"""
    
    def test_coletar_arquivos_e_diretorios_combinacoes(self):
        """Teste cobrindo cenários de diretórios aninhados e arquivos com/sem extensões"""
        # Arrange
        mock_arquivo_py = MagicMock()
        mock_arquivo_py.type = "file"
        mock_arquivo_py.path = "src/main.py"
        mock_arquivo_py.name = "main.py"
        
        mock_arquivo_txt = MagicMock()
        mock_arquivo_txt.type = "file"
        mock_arquivo_txt.path = "docs/readme.txt"
        mock_arquivo_txt.name = "readme.txt"
        
        mock_diretorio = MagicMock()
        mock_diretorio.type = "dir"
        mock_diretorio.path = "src/utils"
        
        mock_dockerfile = MagicMock()
        mock_dockerfile.type = "file"
        mock_dockerfile.path = "docker/Dockerfile"
        mock_dockerfile.name = "Dockerfile"
        
        conteudos = [mock_arquivo_py, mock_arquivo_txt, mock_diretorio, mock_dockerfile]
        extensoes_alvo = [".py", "Dockerfile"]
        
        # Act
        arquivos, diretorios = coletar_arquivos_e_diretorios(conteudos, extensoes_alvo)
        
        # Assert
        assert len(arquivos) == 2
        assert mock_arquivo_py in arquivos
        assert mock_dockerfile in arquivos
        assert mock_arquivo_txt not in arquivos
        
        assert len(diretorios) == 1
        assert "src/utils" in diretorios
    
    def test_coletar_arquivos_e_diretorios_lista_vazia(self):
        """Teste com lista de conteúdos vazia"""
        # Arrange
        conteudos = []
        extensoes_alvo = [".py"]
        
        # Act
        arquivos, diretorios = coletar_arquivos_e_diretorios(conteudos, extensoes_alvo)
        
        # Assert
        assert len(arquivos) == 0
        assert len(diretorios) == 0


class TestLeituraIterativaComParalelismoERetry:
    """Testes para a função leitura_iterativa_com_paralelismo_e_retry"""
    
    @patch('tools.github_reader.concurrent.futures.ThreadPoolExecutor')
    def test_leitura_iterativa_com_paralelismo_e_retry_sucesso(self, mock_executor_class):
        """Teste de leitura iterativa bem-sucedida"""
        # Arrange
        mock_repo = MagicMock()
        mock_arquivo = MagicMock()
        mock_arquivo.type = "file"
        mock_arquivo.path = "src/main.py"
        mock_arquivo.name = "main.py"
        
        mock_repo.get_contents.return_value = [mock_arquivo]
        
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        
        mock_future = MagicMock()
        mock_future.result.return_value = "conteudo do arquivo"
        mock_executor.submit.return_value = mock_future
        mock_executor.as_completed = mock.Mock(return_value=[mock_future])
        
        with patch('tools.github_reader.concurrent.futures.as_completed', return_value=[mock_future]):
            # Act
            resultado = leitura_iterativa_com_paralelismo_e_retry(
                mock_repo, [".py"], "", max_workers=2
            )
        
        # Assert
        assert "src/main.py" in resultado
        assert resultado["src/main.py"] == "conteudo do arquivo"
        mock_repo.get_contents.assert_called_with("")
    
    def test_leitura_iterativa_com_paralelismo_e_retry_erro_ao_listar_conteudo(self):
        """Teste para garantir que erros ao listar diretórios são tratados"""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_contents.side_effect = Exception("Erro ao acessar diretório")
        
        # Act
        resultado = leitura_iterativa_com_paralelismo_e_retry(
            mock_repo, [".py"], "", max_workers=2
        )
        
        # Assert
        assert resultado == {}
        mock_repo.get_contents.assert_called_once_with("")
    
    def test_leitura_iterativa_com_paralelismo_e_retry_max_depth(self):
        """Teste para validar limitação de profundidade"""
        # Arrange
        mock_repo = MagicMock()
        mock_diretorio = MagicMock()
        mock_diretorio.type = "dir"
        mock_diretorio.path = "nivel1"
        
        mock_repo.get_contents.return_value = [mock_diretorio]
        
        # Act
        resultado = leitura_iterativa_com_paralelismo_e_retry(
            mock_repo, [".py"], "", max_workers=2, max_depth=0
        )
        
        # Assert
        assert resultado == {}
        # Deve chamar get_contents apenas uma vez para o diretório raiz
        mock_repo.get_contents.assert_called_once_with("")


class TestLerArquivosRepositorioGithub:
    """Testes para a função ler_arquivos_repositorio_github"""
    
    @patch('tools.github_reader.conectar_ao_github')
    @patch('tools.github_reader.leitura_iterativa_com_paralelismo_e_retry')
    def test_ler_arquivos_repositorio_github_sucesso(self, mock_leitura, mock_conectar):
        """Teste de leitura bem-sucedida de arquivos do repositório"""
        # Arrange
        mock_repo = MagicMock()
        mock_conectar.return_value = mock_repo
        mock_leitura.return_value = {"src/main.py": "conteudo"}
        
        # Act
        resultado = ler_arquivos_repositorio_github("owner/repo", "python")
        
        # Assert
        assert resultado == {"src/main.py": "conteudo"}
        mock_conectar.assert_called_once_with(repositorio_nome="owner/repo")
        mock_leitura.assert_called_once_with(
            mock_repo, [".py"], max_workers=4, max_depth=None
        )
    
    def test_ler_arquivos_repositorio_github_tipo_analise_desconhecido(self):
        """Teste para validar comportamento com tipo de análise não mapeado"""
        # Arrange
        with patch('tools.github_reader.conectar_ao_github') as mock_conectar:
            with patch('tools.github_reader.leitura_iterativa_com_paralelismo_e_retry') as mock_leitura:
                mock_repo = MagicMock()
                mock_conectar.return_value = mock_repo
                mock_leitura.return_value = {}
                
                # Act
                resultado = ler_arquivos_repositorio_github("owner/repo", "tipo_inexistente")
                
                # Assert
                assert resultado == {}
                mock_leitura.assert_called_once_with(
                    mock_repo, None, max_workers=4, max_depth=None
                )
    
    @patch('tools.github_reader.conectar_ao_github')
    def test_ler_arquivos_repositorio_github_erro_conexao(self, mock_conectar):
        """Teste para tratar erro de conexão"""
        # Arrange
        mock_conectar.side_effect = ValueError("Erro de conexão")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Erro de conexão"):
            ler_arquivos_repositorio_github("owner/repo", "python")


class TestObterArquivosParaAnalise:
    """Testes para a função obter_arquivos_para_analise"""
    
    @patch('tools.github_reader.ler_arquivos_repositorio_github')
    def test_obter_arquivos_para_analise(self, mock_ler_arquivos):
        """Teste da função wrapper obter_arquivos_para_analise"""
        # Arrange
        mock_ler_arquivos.return_value = {"test.py": "conteudo"}
        
        # Act
        resultado = obter_arquivos_para_analise("owner/repo", "python", max_workers=2, max_depth=5)
        
        # Assert
        assert resultado == {"test.py": "conteudo"}
        mock_ler_arquivos.assert_called_once_with(
            "owner/repo", "python", max_workers=2, max_depth=5
        )


class TestConstantesEMapeamentos:
    """Testes para validar constantes e mapeamentos"""
    
    def test_tipo_extensoes_mapeamento_estrutura(self):
        """Teste para validar estrutura do mapeamento de extensões"""
        # Assert
        assert isinstance(TIPO_EXTENSOES_MAPEAMENTO, dict)
        assert "python" in TIPO_EXTENSOES_MAPEAMENTO
        assert "terraform" in TIPO_EXTENSOES_MAPEAMENTO
        assert "docker" in TIPO_EXTENSOES_MAPEAMENTO
        
        # Validar que as extensões são listas
        for tipo, extensoes in TIPO_EXTENSOES_MAPEAMENTO.items():
            assert isinstance(extensoes, list)
            assert len(extensoes) > 0
    
    def test_constantes_retry(self):
        """Teste para validar constantes de retry"""
        # Assert
        assert isinstance(MAX_RETRIES, int)
        assert MAX_RETRIES > 0
        assert isinstance(RETRY_DELAY, (int, float))
        assert RETRY_DELAY > 0
