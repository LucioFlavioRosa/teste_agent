import re
from github import Github
from github.Auth import Token
from google.colab import userdata
import logging
import concurrent.futures
from typing import Dict, Any, List, Optional
import time
from core.analysis_registry import AnalysisRegistry

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

MAX_RETRIES = 3
RETRY_DELAY = 2  # segundos
MAX_PARALLELISM = 4  # Limite para evitar throttling da API

class GitHubReader:
    """Leitor de repositórios GitHub com suporte a tipos de análise dinâmicos."""
    
    def __init__(self):
        self.analysis_registry = AnalysisRegistry()
    
    def conectar_ao_github(self, repositorio_nome: str):
        """Estabelece conexão com o repositório GitHub."""
        try:
            GITHUB_TOKEN = userdata.get('github_token')
            if not GITHUB_TOKEN:
                logging.error("Token do GitHub não encontrado em userdata.")
                raise ValueError("Token do GitHub não encontrado.")
            
            auth = Token(GITHUB_TOKEN)
            github_client = Github(auth=auth)
            repositorio = github_client.get_repo(repositorio_nome)
            
            logging.info(f"Conexão bem-sucedida com o repositório: {repositorio_nome}")
            return repositorio
            
        except Exception as e:
            logging.error(f"Erro ao conectar ao GitHub para o repositório '{repositorio_nome}': {e}")
            raise
    
    def arquivo_esta_na_lista_de_extensoes(self, arquivo_obj, extensoes_alvo: List[str]):
        """Verifica se um arquivo corresponde às extensões desejadas."""
        if extensoes_alvo is None:
            return True
        
        return (any(arquivo_obj.path.endswith(ext) for ext in extensoes_alvo) or 
                arquivo_obj.name in extensoes_alvo)
    
    def ler_conteudo_arquivo_com_retry(self, arquivo_obj):
        """Lê o conteúdo de um arquivo com retry em caso de falha."""
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
        """Separa arquivos e diretórios do conteúdo obtido."""
        arquivos = []
        diretorios = []
        
        for item in conteudos:
            if item.type == "dir":
                diretorios.append(item.path)
            else:
                if self.arquivo_esta_na_lista_de_extensoes(item, extensoes_alvo):
                    arquivos.append(item)
        
        return arquivos, diretorios
    
    def leitura_iterativa_com_paralelismo_e_retry(self, repo, extensoes_alvo: List[str], 
                                                  caminho_inicial="", max_workers=MAX_PARALLELISM, 
                                                  max_depth: Optional[int]=None):
        """Percorre o repositório de forma iterativa e paraleliza leitura de arquivos e diretórios."""
        arquivos_do_repo = {}
        caminhos_a_explorar = [(caminho_inicial, 0)]
        
        while caminhos_a_explorar:
            caminho_atual, profundidade = caminhos_a_explorar.pop()
            
            if max_depth is not None and profundidade > max_depth:
                continue
            
            try:
                conteudos = repo.get_contents(caminho_atual)
            except Exception as e:
                logging.error(f"Erro ao obter conteúdo em '{caminho_atual}': {type(e).__name__}: {e}")
                continue
            
            arquivos, diretorios = self.coletar_arquivos_e_diretorios(conteudos, extensoes_alvo)
            
            # Paralelização da leitura de arquivos
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futuros = {executor.submit(self.ler_conteudo_arquivo_com_retry, arquivo): arquivo 
                          for arquivo in arquivos}
                
                for futuro in concurrent.futures.as_completed(futuros):
                    arquivo = futuros[futuro]
                    conteudo = futuro.result()
                    if conteudo is not None:
                        arquivos_do_repo[arquivo.path] = conteudo
            
            # Adicionar diretórios para exploração
            caminhos_a_explorar.extend([(d, profundidade + 1) for d in diretorios])
        
        return arquivos_do_repo
    
    def ler_arquivos_repositorio_github(self, repositorio_nome: str, tipo_analise: str, 
                                       max_workers: int = MAX_PARALLELISM, 
                                       max_depth: Optional[int] = None):
        """Lê arquivos do repositório GitHub baseado no tipo de análise."""
        try:
            repositorio = self.conectar_ao_github(repositorio_nome=repositorio_nome)
            
            # Obter extensões do registro dinâmico
            extensoes_alvo = self.analysis_registry.get_extensions_for_analysis(tipo_analise)
            
            if not extensoes_alvo:
                logging.warning(f"Nenhuma extensão encontrada para o tipo de análise '{tipo_analise}'")
                return {}
            
            arquivos_encontrados = self.leitura_iterativa_com_paralelismo_e_retry(
                repositorio, extensoes_alvo, max_workers=max_workers, max_depth=max_depth
            )
            
            logging.info(f"Arquivos encontrados para análise '{tipo_analise}': {list(arquivos_encontrados.keys())}")
            return arquivos_encontrados
            
        except Exception as e:
            logging.error(f"Erro ao ler arquivos do GitHub para análise '{tipo_analise}': {e}")
            raise

# Instância global para compatibilidade
_github_reader = GitHubReader()

# Funções de compatibilidade
def conectar_ao_github(repositorio_nome: str):
    """Função de compatibilidade."""
    return _github_reader.conectar_ao_github(repositorio_nome)

def arquivo_esta_na_lista_de_extensoes(arquivo_obj, extensoes_alvo: List[str]):
    """Função de compatibilidade."""
    return _github_reader.arquivo_esta_na_lista_de_extensoes(arquivo_obj, extensoes_alvo)

def ler_conteudo_arquivo_com_retry(arquivo_obj):
    """Função de compatibilidade."""
    return _github_reader.ler_conteudo_arquivo_com_retry(arquivo_obj)

def coletar_arquivos_e_diretorios(conteudos, extensoes_alvo: List[str]):
    """Função de compatibilidade."""
    return _github_reader.coletar_arquivos_e_diretorios(conteudos, extensoes_alvo)

def leitura_iterativa_com_paralelismo_e_retry(repo, extensoes_alvo: List[str], caminho_inicial="", max_workers=MAX_PARALLELISM, max_depth: Optional[int]=None):
    """Função de compatibilidade."""
    return _github_reader.leitura_iterativa_com_paralelismo_e_retry(repo, extensoes_alvo, caminho_inicial, max_workers, max_depth)

def ler_arquivos_repositorio_github(repositorio_nome: str, tipo_analise: str, max_workers: int = MAX_PARALLELISM, max_depth: Optional[int] = None):
    """Função de compatibilidade."""
    return _github_reader.ler_arquivos_repositorio_github(repositorio_nome, tipo_analise, max_workers, max_depth)

def obter_arquivos_para_analise(repo_nome: str, tipo_analise: str, max_workers: int = MAX_PARALLELISM, max_depth: Optional[int] = None):
    """Função de compatibilidade."""
    return _github_reader.ler_arquivos_repositorio_github(repo_nome, tipo_analise, max_workers, max_depth)