import re
from github import Github
from github.Auth import Token
from google.colab import userdata
import logging
import concurrent.futures
from typing import Dict, Any, List, Optional
import time
import json
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

MAX_RETRIES = 3
RETRY_DELAY = 2
MAX_PARALLELISM = 4

class ConfiguradorTiposAnalise:
    def __init__(self, caminho_config: Optional[str] = None):
        self.mapeamento_padrao = {
            "terraform": [".tf", ".tfvars"],
            "python": [".py"],
            "cloudformation": [".json", ".yaml", ".yml"],
            "ansible": [".yml", ".yaml"],
            "docker": ["Dockerfile"],
        }
        self.mapeamento = self._carregar_configuracao(caminho_config)
    
    def _carregar_configuracao(self, caminho_config: Optional[str]) -> Dict[str, List[str]]:
        if caminho_config and os.path.exists(caminho_config):
            try:
                with open(caminho_config, 'r', encoding='utf-8') as f:
                    config_externa = json.load(f)
                    return {**self.mapeamento_padrao, **config_externa}
            except Exception as e:
                logging.warning(f"Erro ao carregar configuração externa: {e}. Usando configuração padrão.")
        return self.mapeamento_padrao
    
    def obter_extensoes(self, tipo_analise: str) -> Optional[List[str]]:
        return self.mapeamento.get(tipo_analise.lower())

class ConectorGitHub:
    def conectar(self, repositorio_nome: str):
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
        except (ValueError, RuntimeError) as e:
            logging.error(f"Erro ao conectar ao GitHub para o repositório '{repositorio_nome}': {e}")
            raise
        except KeyError as e:
            logging.error(f"Erro de chave ao conectar ao GitHub: {e}")
            raise
        except TypeError as e:
            logging.error(f"Erro de tipo ao conectar ao GitHub: {e}")
            raise

class FiltroArquivos:
    @staticmethod
    def arquivo_esta_na_lista_de_extensoes(arquivo_obj, extensoes_alvo: List[str]):
        if extensoes_alvo is None:
            return True
        if any(arquivo_obj.path.endswith(ext) for ext in extensoes_alvo) or arquivo_obj.name in extensoes_alvo:
            return True
        return False
    
    @staticmethod
    def coletar_arquivos_e_diretorios(conteudos, extensoes_alvo: List[str]):
        arquivos = []
        diretorios = []
        for item in conteudos:
            if item.type == "dir":
                diretorios.append(item.path)
            else:
                if FiltroArquivos.arquivo_esta_na_lista_de_extensoes(item, extensoes_alvo):
                    arquivos.append(item)
        return arquivos, diretorios

class LeitorArquivos:
    @staticmethod
    def ler_conteudo_arquivo_com_retry(arquivo_obj):
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

class ExploradorRepositorio:
    def __init__(self, conector: ConectorGitHub, filtro: FiltroArquivos, leitor: LeitorArquivos):
        self.conector = conector
        self.filtro = filtro
        self.leitor = leitor
    
    def leitura_iterativa_com_paralelismo_e_retry(self, repo, extensoes_alvo: List[str], caminho_inicial="", max_workers=MAX_PARALLELISM, max_depth: Optional[int]=None):
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
            arquivos, diretorios = self.filtro.coletar_arquivos_e_diretorios(conteudos, extensoes_alvo)
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futuros = {executor.submit(self.leitor.ler_conteudo_arquivo_com_retry, arquivo): arquivo for arquivo in arquivos}
                for futuro in concurrent.futures.as_completed(futuros):
                    arquivo = futuros[futuro]
                    conteudo = futuro.result()
                    if conteudo is not None:
                        arquivos_do_repo[arquivo.path] = conteudo
            caminhos_a_explorar.extend([(d, profundidade + 1) for d in diretorios])
        return arquivos_do_repo

class LeitorRepositorioGitHub:
    def __init__(self, configurador: ConfiguradorTiposAnalise = None):
        self.configurador = configurador or ConfiguradorTiposAnalise()
        self.conector = ConectorGitHub()
        self.filtro = FiltroArquivos()
        self.leitor = LeitorArquivos()
        self.explorador = ExploradorRepositorio(self.conector, self.filtro, self.leitor)
    
    def ler_arquivos(self, repositorio_nome: str, tipo_analise: str, max_workers: int = MAX_PARALLELISM, max_depth: Optional[int] = None):
        try:
            repositorio = self.conector.conectar(repositorio_nome=repositorio_nome)
            extensoes_alvo = self.configurador.obter_extensoes(tipo_analise)
            arquivos_encontrados = self.explorador.leitura_iterativa_com_paralelismo_e_retry(repositorio, extensoes_alvo, max_workers=max_workers, max_depth=max_depth)
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

_leitor_global = LeitorRepositorioGitHub()

def obter_arquivos_para_analise(repo_nome: str, tipo_analise: str, max_workers: int = MAX_PARALLELISM, max_depth: Optional[int] = None):
    return _leitor_global.ler_arquivos(repo_nome, tipo_analise, max_workers=max_workers, max_depth=max_depth)