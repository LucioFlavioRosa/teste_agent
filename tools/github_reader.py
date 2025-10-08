import re
from github import Github
from github.Auth import Token
from google.colab import userdata
import logging
import concurrent.futures
from typing import Dict, Any, List, Optional
import time
from interfaces.repositorio_reader_interface import IRepositorioReader
from services.github_connector import GitHubConnector
from services.arquivo_processor import ArquivoProcessor
from services.registro_tipos_analise import RegistroTiposAnalise

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

MAX_RETRIES = 3
RETRY_DELAY = 2  # segundos
MAX_PARALLELISM = 4  # Limite para evitar throttling da API

class GitHubReader(IRepositorioReader):
    def __init__(self):
        self.connector = GitHubConnector()
        self.processor = ArquivoProcessor()
        self.registro_tipos = RegistroTiposAnalise()
    
    def obter_arquivos_para_analise(self, repo_nome: str, tipo_analise: str, 
                                   max_workers: int = MAX_PARALLELISM, 
                                   max_depth: Optional[int] = None) -> Dict[str, str]:
        """Obtém arquivos do repositório para análise"""
        try:
            repositorio = self.connector.conectar_ao_github(repo_nome)
            extensoes_alvo = self.registro_tipos.obter_extensoes_tipo(tipo_analise)
            
            arquivos_encontrados = self._leitura_iterativa_com_paralelismo_e_retry(
                repositorio, extensoes_alvo, max_workers=max_workers, max_depth=max_depth
            )
            
            logging.info(f"Arquivos encontrados para análise '{tipo_analise}': {list(arquivos_encontrados.keys())}")
            return arquivos_encontrados
            
        except (ValueError, RuntimeError, KeyError, TypeError) as e:
            logging.error(f"Erro ao ler arquivos do GitHub para análise '{tipo_analise}': {e}")
            raise
    
    def _leitura_iterativa_com_paralelismo_e_retry(self, repo, extensoes_alvo: List[str], 
                                                  caminho_inicial="", max_workers=MAX_PARALLELISM, 
                                                  max_depth: Optional[int] = None):
        """Percorre o repositório de forma iterativa e paraleliza leitura de arquivos"""
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
            
            arquivos, diretorios = self.processor.coletar_arquivos_e_diretorios(conteudos, extensoes_alvo)
            
            # Processamento paralelo dos arquivos
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futuros = {executor.submit(self.processor.ler_conteudo_arquivo_com_retry, arquivo): arquivo 
                          for arquivo in arquivos}
                
                for futuro in concurrent.futures.as_completed(futuros):
                    arquivo = futuros[futuro]
                    conteudo = futuro.result()
                    if conteudo is not None:
                        arquivos_do_repo[arquivo.path] = conteudo
            
            caminhos_a_explorar.extend([(d, profundidade + 1) for d in diretorios])
        
        return arquivos_do_repo

# Instância global para compatibilidade
_github_reader = GitHubReader()

def obter_arquivos_para_analise(repo_nome: str, tipo_analise: str, 
                               max_workers: int = MAX_PARALLELISM, 
                               max_depth: Optional[int] = None):
    """Função de compatibilidade para manter a interface existente"""
    return _github_reader.obter_arquivos_para_analise(repo_nome, tipo_analise, max_workers, max_depth)