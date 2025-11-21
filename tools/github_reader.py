import re
from github import Github
from github.Auth import Token
from google.colab import userdata
import logging
import concurrent.futures
from typing import Dict, Any, List, Optional, Protocol
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

TIPO_EXTENSOES_MAPEAMENTO = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}

MAX_RETRIES = 3
RETRY_DELAY = 2  # segundos
MAX_PARALLELISM = 4  # Limite para evitar throttling da API


@dataclass
class ReaderConfig:
    """Configuração para leitura de repositórios."""
    max_workers: int = MAX_PARALLELISM
    max_depth: Optional[int] = None
    max_retries: int = MAX_RETRIES
    retry_delay: int = RETRY_DELAY


class AuthenticationService(ABC):
    """Interface abstrata para serviços de autenticação."""
    
    @abstractmethod
    def get_token(self) -> str:
        """Obtém o token de autenticação."""
        pass


class ColabAuthenticationService(AuthenticationService):
    """Implementação do serviço de autenticação para Google Colab."""
    
    def get_token(self) -> str:
        """Obtém o token do GitHub a partir do userdata do Colab."""
        try:
            token = userdata.get('github_token')
            if not token:
                raise ValueError("Token do GitHub não encontrado em userdata.")
            return token
        except Exception as e:
            logging.error(f"Erro ao obter token de autenticação: {e}")
            raise


class RepositoryClient(Protocol):
    """Interface para clientes de repositório."""
    
    def get_contents(self, path: str = ""):
        """Obtém o conteúdo de um caminho no repositório."""
        pass


class GitHubRepositoryClient:
    """Cliente para repositórios GitHub."""
    
    def __init__(self, auth_service: AuthenticationService):
        self._auth_service = auth_service
        self._repo = None
    
    def connect_to_repository(self, repository_name: str) -> RepositoryClient:
        """Conecta ao repositório GitHub especificado."""
        try:
            token = self._auth_service.get_token()
            auth = Token(token)
            github_client = Github(auth=auth)
            self._repo = github_client.get_repo(repository_name)
            logging.info(f"Conexão bem-sucedida com o repositório: {repository_name}")
            return self._repo
        except Exception as e:
            logging.error(f"Erro ao conectar ao repositório '{repository_name}': {e}")
            raise


class ExtensionMapper:
    """Responsável por mapear tipos de análise para extensões de arquivo."""
    
    def __init__(self, mapping: Dict[str, List[str]] = None):
        self._mapping = mapping or TIPO_EXTENSOES_MAPEAMENTO
    
    def get_extensions_for_analysis(self, analysis_type: str) -> List[str]:
        """Obtém as extensões de arquivo para um tipo de análise."""
        return self._mapping.get(analysis_type.lower())
    
    def is_file_in_extensions(self, file_obj, target_extensions: List[str]) -> bool:
        """Verifica se um arquivo está na lista de extensões alvo."""
        if target_extensions is None:
            return True
        return (any(file_obj.path.endswith(ext) for ext in target_extensions) or 
                file_obj.name in target_extensions)


class FileContentReader:
    """Responsável por ler o conteúdo de arquivos com retry."""
    
    def __init__(self, config: ReaderConfig):
        self._config = config
    
    def read_file_content_with_retry(self, file_obj) -> Optional[str]:
        """Lê o conteúdo de um arquivo com retry em caso de falha."""
        for attempt in range(1, self._config.max_retries + 1):
            try:
                content = file_obj.decoded_content.decode('utf-8')
                return content
            except AttributeError as e:
                logging.error(f"Arquivo sem conteúdo decodificável '{file_obj.path}': {e}")
                return None
            except Exception as e:
                logging.error(f"Erro na decodificação de '{file_obj.path}' (tentativa {attempt}/{self._config.max_retries}): {type(e).__name__}: {e}")
                if attempt < self._config.max_retries:
                    time.sleep(self._config.retry_delay)
                else:
                    return None


class DirectoryExplorer:
    """Responsável por explorar diretórios e coletar arquivos."""
    
    def __init__(self, extension_mapper: ExtensionMapper):
        self._extension_mapper = extension_mapper
    
    def collect_files_and_directories(self, contents, target_extensions: List[str]):
        """Coleta arquivos e diretórios de um conteúdo de repositório."""
        files = []
        directories = []
        for item in contents:
            if item.type == "dir":
                directories.append(item.path)
            else:
                if self._extension_mapper.is_file_in_extensions(item, target_extensions):
                    files.append(item)
        return files, directories


class ParallelRepositoryReader:
    """Responsável por ler repositórios de forma paralela e iterativa."""
    
    def __init__(self, file_reader: FileContentReader, directory_explorer: DirectoryExplorer, config: ReaderConfig):
        self._file_reader = file_reader
        self._directory_explorer = directory_explorer
        self._config = config
    
    def read_repository_iteratively(self, repo: RepositoryClient, target_extensions: List[str], initial_path: str = "") -> Dict[str, str]:
        """Percorre o repositório de forma iterativa e paralela."""
        repository_files = {}
        paths_to_explore = [(initial_path, 0)]
        
        while paths_to_explore:
            current_path, depth = paths_to_explore.pop()
            if self._config.max_depth is not None and depth > self._config.max_depth:
                continue
            
            try:
                contents = repo.get_contents(current_path)
            except Exception as e:
                logging.error(f"Erro ao obter conteúdo em '{current_path}': {type(e).__name__}: {e}")
                continue
            
            files, directories = self._directory_explorer.collect_files_and_directories(contents, target_extensions)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self._config.max_workers) as executor:
                futures = {executor.submit(self._file_reader.read_file_content_with_retry, file): file for file in files}
                for future in concurrent.futures.as_completed(futures):
                    file = futures[future]
                    content = future.result()
                    if content is not None:
                        repository_files[file.path] = content
            
            paths_to_explore.extend([(d, depth + 1) for d in directories])
        
        return repository_files


class RepositoryAnalysisLogger:
    """Responsável por fazer logging dos resultados da análise."""
    
    def log_analysis_results(self, analysis_type: str, found_files: Dict[str, str]):
        """Registra os resultados da análise no log."""
        logging.info(f"Arquivos encontrados para análise '{analysis_type}': {list(found_files.keys())}")


class GitHubRepositoryAnalyzer:
    """Classe principal que orquestra a análise de repositórios GitHub."""
    
    def __init__(self, 
                 repository_client: GitHubRepositoryClient,
                 extension_mapper: ExtensionMapper,
                 file_reader: FileContentReader,
                 directory_explorer: DirectoryExplorer,
                 parallel_reader: ParallelRepositoryReader,
                 logger: RepositoryAnalysisLogger):
        self._repository_client = repository_client
        self._extension_mapper = extension_mapper
        self._parallel_reader = parallel_reader
        self._logger = logger
    
    def analyze_repository(self, repository_name: str, analysis_type: str) -> Dict[str, str]:
        """Analisa um repositório GitHub para um tipo específico de análise."""
        try:
            repo = self._repository_client.connect_to_repository(repository_name)
            target_extensions = self._extension_mapper.get_extensions_for_analysis(analysis_type)
            found_files = self._parallel_reader.read_repository_iteratively(repo, target_extensions)
            self._logger.log_analysis_results(analysis_type, found_files)
            return found_files
        except Exception as e:
            logging.error(f"Erro ao analisar repositório '{repository_name}' para análise '{analysis_type}': {e}")
            raise


# Funções de conveniência para manter compatibilidade com a API existente
def conectar_ao_github(repositorio_nome: str):
    """Função de compatibilidade - conecta ao GitHub usando implementação legacy."""
    auth_service = ColabAuthenticationService()
    client = GitHubRepositoryClient(auth_service)
    return client.connect_to_repository(repositorio_nome)


def arquivo_esta_na_lista_de_extensoes(arquivo_obj, extensoes_alvo: List[str]):
    """Função de compatibilidade - verifica se arquivo está nas extensões alvo."""
    mapper = ExtensionMapper()
    return mapper.is_file_in_extensions(arquivo_obj, extensoes_alvo)


def ler_conteudo_arquivo_com_retry(arquivo_obj):
    """Função de compatibilidade - lê conteúdo de arquivo com retry."""
    config = ReaderConfig()
    reader = FileContentReader(config)
    return reader.read_file_content_with_retry(arquivo_obj)


def coletar_arquivos_e_diretorios(conteudos, extensoes_alvo: List[str]):
    """Função de compatibilidade - coleta arquivos e diretórios."""
    mapper = ExtensionMapper()
    explorer = DirectoryExplorer(mapper)
    return explorer.collect_files_and_directories(conteudos, extensoes_alvo)


def leitura_iterativa_com_paralelismo_e_retry(repo, extensoes_alvo: List[str], caminho_inicial="", max_workers=MAX_PARALLELISM, max_depth: Optional[int]=None):
    """Função de compatibilidade - leitura iterativa com paralelismo."""
    config = ReaderConfig(max_workers=max_workers, max_depth=max_depth)
    file_reader = FileContentReader(config)
    mapper = ExtensionMapper()
    explorer = DirectoryExplorer(mapper)
    parallel_reader = ParallelRepositoryReader(file_reader, explorer, config)
    return parallel_reader.read_repository_iteratively(repo, extensoes_alvo, caminho_inicial)


def ler_arquivos_repositorio_github(repositorio_nome: str, tipo_analise: str, max_workers: int = MAX_PARALLELISM, max_depth: Optional[int] = None):
    """Função de compatibilidade - lê arquivos do repositório GitHub."""
    try:
        config = ReaderConfig(max_workers=max_workers, max_depth=max_depth)
        auth_service = ColabAuthenticationService()
        repository_client = GitHubRepositoryClient(auth_service)
        extension_mapper = ExtensionMapper()
        file_reader = FileContentReader(config)
        directory_explorer = DirectoryExplorer(extension_mapper)
        parallel_reader = ParallelRepositoryReader(file_reader, directory_explorer, config)
        logger = RepositoryAnalysisLogger()
        
        analyzer = GitHubRepositoryAnalyzer(
            repository_client, extension_mapper, file_reader, 
            directory_explorer, parallel_reader, logger
        )
        
        return analyzer.analyze_repository(repositorio_nome, tipo_analise)
    except Exception as e:
        logging.error(f"Erro ao ler arquivos do GitHub para análise '{tipo_analise}': {e}")
        raise


def obter_arquivos_para_analise(repo_nome: str, tipo_analise: str, max_workers: int = MAX_PARALLELISM, max_depth: Optional[int] = None):
    """Função principal para obter arquivos para análise."""
    return ler_arquivos_repositorio_github(repo_nome, tipo_analise, max_workers=max_workers, max_depth=max_depth)
