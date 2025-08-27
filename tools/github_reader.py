import re
from github import Github
from github.Auth import Token
from core.config_provider import ConfigFactory, ConfigProvider
from core.analysis_registry import AnalysisRegistry
import logging
import concurrent.futures
from typing import Dict, Any, List, Optional
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

MAX_RETRIES = 3
RETRY_DELAY = 2  # segundos
MAX_PARALLELISM = 4  # Limite para evitar throttling da API

class GitHubReaderConfig:
    """Configuração específica para leitura do GitHub."""
    def __init__(self, max_workers: int = MAX_PARALLELISM, max_depth: Optional[int] = None):
        self.max_workers = max_workers
        self.max_depth = max_depth

class GitHubReader:
    """Classe responsável pela leitura de repositórios GitHub."""
    
    def __init__(self, config_provider: ConfigProvider = None):
        self.config_provider = config_provider or ConfigFactory.create_provider()
        self.analysis_registry = AnalysisRegistry()
    
    def conectar_ao_github(self, repositorio_nome: str):
        """Conecta ao repositório GitHub."""
        try:
            github_token = self.config_provider.get_github_token()
            auth = Token(github_token)
            github_client = Github(auth=auth)
            repositorio = github_client.get_repo(repositorio_nome)
            logging.info(f"Conexão bem-sucedida com o repositório: {repositorio_nome}")
            return repositorio
        except (ValueError, RuntimeError) as e:
            logging.error(f"Erro ao conectar ao GitHub para o repositório '{repositorio_nome}': {e}")
            raise
        except KeyError as e:
            logging.error(f"Erro de chave ao conectar ao GitHub: {e}")
            raise
        except TypeError as e:
            logging.error(f"Erro de tipo ao conectar ao GitHub: {e}")
            raise
    
    def arquivo_esta_na_lista_de_extensoes(self, arquivo_obj, extensoes_alvo: List[str]):
        """Verifica se o arquivo está na lista de extensões alvo."""
        if extensoes_alvo is None:
            return True
        if any(arquivo_obj.path.endswith(ext) for ext in extensoes_alvo) or arquivo_obj.name in extensoes_alvo:
            return True
        return False
    
    def ler_conteudo_arquivo_com_retry(self, arquivo_obj):
        """Lê o conteúdo do arquivo com retry em caso de falha."""
        for tentativa in range(1, MAX_RETRIES + 1):
            try:
                conteudo_arquivo = arquivo_obj.decoded_content.decode('utf-8')
                return conteudo_arquivo
            except AttributeError as e:
                logging.error(f"Arquivo sem conteúdo decodificável '{arquivo_obj.path}': {e}")
                return None
            except Exception as e:
                logging.error(f"Erro inesperado na decodificação de '{arquivo_obj.path}' (tentativa {tentativa}/{MAX_RETRIES}): {type(e).__name__}: {e}")
                if tentativa < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                else:
                    return None
    
    def coletar_arquivos_e_diretorios(self, conteudos, extensoes_alvo: List[str]):
        """Coleta arquivos e diretórios do conteúdo do repositório."""
        arquivos = []
        diretorios = []
        for item in conteudos:
            if item.type == "dir":
                diretorios.append(item.path)
            else:
                if self.arquivo_esta_na_lista_de_extensoes(item, extensoes_alvo):
                    arquivos.append(item)
        return arquivos, diretorios
    
    def leitura_iterativa_com_paralelismo_e_retry(self, repo, extensoes_alvo: List[str], config: GitHubReaderConfig, caminho_inicial=""):
        """Percorre o repositório de forma iterativa e paraleliza leitura de arquivos e diretórios."""
        arquivos_do_repo = {}
        caminhos_a_explorar = [(caminho_inicial, 0)]
        while caminhos_a_explorar:
            caminho_atual, profundidade = caminhos_a_explorar.pop()
            if config.max_depth is not None and profundidade > config.max_depth:
                continue
            try:
                conteudos = repo.get_contents(caminho_atual)
            except Exception as e:
                logging.error(f"Erro ao obter conteúdo em '{caminho_atual}': {type(e).__name__}: {e}")
                continue
            arquivos, diretorios = self.coletar_arquivos_e_diretorios(conteudos, extensoes_alvo)
            with concurrent.futures.ThreadPoolExecutor(max_workers=config.max_workers) as executor:
                futuros = {executor.submit(self.ler_conteudo_arquivo_com_retry, arquivo): arquivo for arquivo in arquivos}
                for futuro in concurrent.futures.as_completed(futuros):
                    arquivo = futuros[futuro]
                    conteudo = futuro.result()
                    if conteudo is not None:
                        arquivos_do_repo[arquivo.path] = conteudo
            caminhos_a_explorar.extend([(d, profundidade + 1) for d in diretorios])
        return arquivos_do_repo
    
    def ler_arquivos_repositorio_github(self, repositorio_nome: str, tipo_analise: str, config: GitHubReaderConfig):
        """Lê arquivos do repositório GitHub para análise."""
        try:
            repositorio = self.conectar_ao_github(repositorio_nome=repositorio_nome)
            extensoes_alvo = self.analysis_registry.get_extensions_for_type(tipo_analise)
            arquivos_encontrados = self.leitura_iterativa_com_paralelismo_e_retry(repositorio, extensoes_alvo, config)
            logging.info(f"Arquivos encontrados para análise '{tipo_analise}': {list(arquivos_encontrados.keys())}")
            return arquivos_encontrados
        except ValueError as e:
            logging.error(f"Erro ao ler arquivos do GitHub para análise '{tipo_analise}': {e}")
            raise
        except RuntimeError as e:
            logging.error(f"Erro de execução ao ler arquivos do GitHub: {e}")
            raise
        except KeyError as e:
            logging.error(f"Erro de chave ao ler arquivos do GitHub: {e}")
            raise
        except TypeError as e:
            logging.error(f"Erro de tipo ao ler arquivos do GitHub: {e}")
            raise

# Instância global para compatibilidade
_github_reader = GitHubReader()

def obter_arquivos_para_analise(repo_nome: str, tipo_analise: str, max_workers: int = MAX_PARALLELISM, max_depth: Optional[int] = None):
    """Função de compatibilidade que delega para a instância da classe."""
    config = GitHubReaderConfig(max_workers=max_workers, max_depth=max_depth)
    return _github_reader.ler_arquivos_repositorio_github(repo_nome, tipo_analise, config)