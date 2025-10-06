import pytest
import time
from unittest.mock import patch, MagicMock
from tools.github_reader import (
    conectar_ao_github,
    arquivo_esta_na_lista_de_extensoes,
    ler_conteudo_arquivo_com_retry,
    coletar_arquivos_e_diretorios,
    leitura_iterativa_com_paralelismo_e_retry,
    ler_arquivos_repositorio_github,
    obter_arquivos_para_analise
)


class TestGithubReader:
    """Testes unitários para o módulo github_reader.py"""

    @patch('tools.github_reader.userdata')
    @patch('tools.github_reader.Github')
    def test_conectar_ao_github_sucesso(self, mock_github, mock_userdata):
        """Testa conexão bem-sucedida ao GitHub"""
        mock_userdata.get.return_value = 'fake_token'
        mock_repo = MagicMock()
        mock_github_instance = MagicMock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance
        
        resultado = conectar_ao_github('owner/repo')
        
        assert resultado == mock_repo
        mock_userdata.get.assert_called_once_with('github_token')
        mock_github_instance.get_repo.assert_called_once_with('owner/repo')

    @patch('tools.github_reader.userdata')
    def test_conectar_ao_github_token_invalido(self, mock_userdata):
        """Testa se ValueError é lançado quando o token está ausente"""
        mock_userdata.get.return_value = None
        
        with pytest.raises(ValueError) as exc_info:
            conectar_ao_github('owner/repo')
        
        assert "Token do GitHub não encontrado" in str(exc_info.value)

    def test_arquivo_esta_na_lista_de_extensoes_sucesso(self):
        """Testa verificação de extensão de arquivo - caso positivo"""
        mock_arquivo = MagicMock()
        mock_arquivo.path = 'src/main.py'
        mock_arquivo.name = 'main.py'
        
        resultado = arquivo_esta_na_lista_de_extensoes(mock_arquivo, ['.py', '.js'])
        
        assert resultado is True

    def test_arquivo_esta_na_lista_de_extensoes_falso(self):
        """Testa verificação de extensão de arquivo - caso negativo"""
        mock_arquivo = MagicMock()
        mock_arquivo.path = 'src/main.txt'
        mock_arquivo.name = 'main.txt'
        
        resultado = arquivo_esta_na_lista_de_extensoes(mock_arquivo, ['.py', '.js'])
        
        assert resultado is False

    def test_arquivo_esta_na_lista_de_extensoes_sem_filtro(self):
        """Testa verificação quando não há filtro de extensões"""
        mock_arquivo = MagicMock()
        mock_arquivo.path = 'qualquer_arquivo.xyz'
        
        resultado = arquivo_esta_na_lista_de_extensoes(mock_arquivo, None)
        
        assert resultado is True

    def test_ler_conteudo_arquivo_com_retry_sucesso(self):
        """Testa leitura bem-sucedida de arquivo"""
        mock_arquivo = MagicMock()
        mock_arquivo.decoded_content.decode.return_value = 'conteudo do arquivo'
        mock_arquivo.path = 'test.py'
        
        resultado = ler_conteudo_arquivo_com_retry(mock_arquivo)
        
        assert resultado == 'conteudo do arquivo'
        mock_arquivo.decoded_content.decode.assert_called_once_with('utf-8')

    def test_ler_conteudo_arquivo_com_retry_falha(self):
        """Testa falha na leitura de arquivo após tentativas"""
        mock_arquivo = MagicMock()
        mock_arquivo.decoded_content.decode.side_effect = AttributeError("No decoded_content")
        mock_arquivo.path = 'test.py'
        
        resultado = ler_conteudo_arquivo_com_retry(mock_arquivo)
        
        assert resultado is None

    @patch('tools.github_reader.time.sleep')
    def test_ler_conteudo_arquivo_com_retry_com_tentativas(self, mock_sleep):
        """Testa retry na leitura de arquivo"""
        mock_arquivo = MagicMock()
        mock_arquivo.path = 'test.py'
        # Primeira e segunda tentativas falham, terceira sucede
        mock_arquivo.decoded_content.decode.side_effect = [
            Exception("Network error"),
            Exception("Network error"),
            'conteudo recuperado'
        ]
        
        resultado = ler_conteudo_arquivo_com_retry(mock_arquivo)
        
        assert resultado == 'conteudo recuperado'
        assert mock_sleep.call_count == 2  # Duas tentativas falharam

    def test_coletar_arquivos_e_diretorios(self):
        """Testa coleta e separação de arquivos e diretórios"""
        mock_arquivo1 = MagicMock()
        mock_arquivo1.type = "file"
        mock_arquivo1.path = "src/main.py"
        mock_arquivo1.name = "main.py"
        
        mock_arquivo2 = MagicMock()
        mock_arquivo2.type = "file"
        mock_arquivo2.path = "README.md"
        mock_arquivo2.name = "README.md"
        
        mock_dir = MagicMock()
        mock_dir.type = "dir"
        mock_dir.path = "src/utils"
        
        conteudos = [mock_arquivo1, mock_arquivo2, mock_dir]
        extensoes_alvo = [".py"]
        
        arquivos, diretorios = coletar_arquivos_e_diretorios(conteudos, extensoes_alvo)
        
        assert len(arquivos) == 1
        assert arquivos[0] == mock_arquivo1
        assert len(diretorios) == 1
        assert diretorios[0] == "src/utils"

    @patch('tools.github_reader.concurrent.futures.ThreadPoolExecutor')
    def test_leitura_iterativa_limite_profundidade(self, mock_executor):
        """Testa se o limite de profundidade é respeitado"""
        mock_repo = MagicMock()
        
        # Simular estrutura de diretórios
        mock_conteudo_raiz = []
        mock_dir = MagicMock()
        mock_dir.type = "dir"
        mock_dir.path = "nivel1"
        mock_conteudo_raiz.append(mock_dir)
        
        mock_conteudo_nivel1 = []
        mock_dir_nivel2 = MagicMock()
        mock_dir_nivel2.type = "dir"
        mock_dir_nivel2.path = "nivel1/nivel2"
        mock_conteudo_nivel1.append(mock_dir_nivel2)
        
        mock_repo.get_contents.side_effect = [
            mock_conteudo_raiz,
            mock_conteudo_nivel1
        ]
        
        # Mock do executor para evitar execução paralela real
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        mock_executor_instance.submit.return_value = MagicMock()
        
        resultado = leitura_iterativa_com_paralelismo_e_retry(
            repo=mock_repo,
            extensoes_alvo=[".py"],
            caminho_inicial="",
            max_depth=1
        )
        
        # Deve ter chamado get_contents apenas 2 vezes (raiz + nivel1)
        assert mock_repo.get_contents.call_count == 2
        assert isinstance(resultado, dict)

    @patch('tools.github_reader.conectar_ao_github')
    @patch('tools.github_reader.leitura_iterativa_com_paralelismo_e_retry')
    def test_ler_arquivos_repositorio_github_sucesso(self, mock_leitura, mock_conectar):
        """Testa leitura bem-sucedida de arquivos do repositório"""
        mock_repo = MagicMock()
        mock_conectar.return_value = mock_repo
        mock_leitura.return_value = {'src/main.py': 'codigo python'}
        
        resultado = ler_arquivos_repositorio_github('owner/repo', 'python')
        
        assert resultado == {'src/main.py': 'codigo python'}
        mock_conectar.assert_called_once_with(repositorio_nome='owner/repo')
        mock_leitura.assert_called_once_with(mock_repo, ['.py'], max_workers=4, max_depth=None)

    @patch('tools.github_reader.conectar_ao_github')
    def test_ler_arquivos_repositorio_github_falha_conexao(self, mock_conectar):
        """Testa tratamento de falha na conexão com GitHub"""
        mock_conectar.side_effect = ValueError("Token inválido")
        
        with pytest.raises(ValueError):
            ler_arquivos_repositorio_github('owner/repo', 'python')

    @patch('tools.github_reader.ler_arquivos_repositorio_github')
    def test_obter_arquivos_para_analise(self, mock_ler_arquivos):
        """Testa função wrapper obter_arquivos_para_analise"""
        mock_ler_arquivos.return_value = {'test.py': 'codigo'}
        
        resultado = obter_arquivos_para_analise('owner/repo', 'python')
        
        assert resultado == {'test.py': 'codigo'}
        mock_ler_arquivos.assert_called_once_with('owner/repo', 'python', max_workers=4, max_depth=None)