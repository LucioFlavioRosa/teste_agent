import re
from github import Github
from github.Auth import Token
from tools.config import config
import logging
import concurrent.futures
from typing import Dict, Any, List, Optional
import time

# Configura logging usando a configuração centralizada
config.configure_logging()
logger = logging.getLogger(__name__)

TIPO_EXTENSOES_MAPEAMENTO = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}

def conectar_ao_github(repositorio_nome: str):
    """Conecta ao GitHub usando configuração flexível."""
    try:
        github_config = config.get_github_config()
        
        if not github_config['token']:
            logger.error("Token do GitHub não encontrado na configuração.")
            raise ValueError("Token do GitHub não encontrado.")
        
        auth = Token(github_config['token'])
        github_client = Github(auth=auth, base_url=github_config['api_url'])
        repositorio = github_client.get_repo(repositorio_nome)
        logger.info(f"Conexão bem-sucedida com o repositório: {repositorio_nome}")
        return repositorio
    except (ValueError, RuntimeError) as e:
        logger.error(f"Erro ao conectar ao GitHub para o repositório '{repositorio_nome}': {e}")
        raise
    except KeyError as e:
        logger.error(f"Erro de chave ao conectar ao GitHub: {e}")
        raise
    except TypeError as e:
        logger.error(f"Erro de tipo ao conectar ao GitHub: {e}")
        raise

def arquivo_esta_na_lista_de_extensoes(arquivo_obj, extensoes_alvo: List[str]):
    """Verifica se o arquivo corresponde às extensões desejadas."""
    if extensoes_alvo is None:
        return True
    if any(arquivo_obj.path.endswith(ext) for ext in extensoes_alvo) or arquivo_obj.name in extensoes_alvo:
        return True
    return False

def ler_conteudo_arquivo_com_retry(arquivo_obj):
    """Lê conteúdo do arquivo com retry baseado na configuração."""
    github_config = config.get_github_config()
    max_retries = github_config['max_retries']
    retry_delay = github_config['retry_delay']
    
    for tentativa in range(1, max_retries + 1):
        try:
            conteudo_arquivo = arquivo_obj.decoded_content.decode('utf-8')
            return conteudo_arquivo
        except AttributeError as e:
            logger.error(f"Arquivo sem conteúdo decodificável '{arquivo_obj.path}': {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado na decodificação de '{arquivo_obj.path}' (tentativa {tentativa}/{max_retries}): {type(e).__name__}: {e}")
            if tentativa < max_retries:
                time.sleep(retry_delay)
            else:
                return None

def coletar_arquivos_e_diretorios(conteudos, extensoes_alvo: List[str]):
    """Coleta arquivos e diretórios do conteúdo do repositório."""
    arquivos = []
    diretorios = []
    for item in conteudos:
        if item.type == "dir":
            diretorios.append(item.path)
        else:
            if arquivo_esta_na_lista_de_extensoes(item, extensoes_alvo):
                arquivos.append(item)
    return arquivos, diretorios

def leitura_iterativa_com_paralelismo_e_retry(repo, extensoes_alvo: List[str], caminho_inicial="", max_workers=None, max_depth: Optional[int]=None):
    """
    Percorre o repositório de forma iterativa e paraleliza leitura de arquivos e diretórios.
    Implementa retry para leitura de arquivos e limita paralelismo conforme configuração.
    """
    if max_workers is None:
        github_config = config.get_github_config()
        max_workers = github_config['max_parallelism']
    
    if max_depth is None:
        analysis_config = config.get_analysis_config()
        max_depth = analysis_config['max_depth']
    
    arquivos_do_repo = {}
    caminhos_a_explorar = [(caminho_inicial, 0)]
    
    while caminhos_a_explorar:
        caminho_atual, profundidade = caminhos_a_explorar.pop()
        if max_depth is not None and profundidade > max_depth:
            continue
        try:
            conteudos = repo.get_contents(caminho_atual)
        except Exception as e:
            logger.error(f"Erro ao obter conteúdo em '{caminho_atual}': {type(e).__name__}: {e}")
            continue
        
        arquivos, diretorios = coletar_arquivos_e_diretorios(conteudos, extensoes_alvo)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futuros = {executor.submit(ler_conteudo_arquivo_com_retry, arquivo): arquivo for arquivo in arquivos}
            for futuro in concurrent.futures.as_completed(futuros):
                arquivo = futuros[futuro]
                conteudo = futuro.result()
                if conteudo is not None:
                    arquivos_do_repo[arquivo.path] = conteudo
        
        caminhos_a_explorar.extend([(d, profundidade + 1) for d in diretorios])
    
    return arquivos_do_repo

def ler_arquivos_repositorio_github(repositorio_nome: str, tipo_analise: str, max_workers: int = None, max_depth: Optional[int] = None):
    """Lê arquivos do repositório GitHub com configuração flexível."""
    try:
        repositorio = conectar_ao_github(repositorio_nome=repositorio_nome)
        extensoes_alvo = TIPO_EXTENSOES_MAPEAMENTO.get(tipo_analise.lower())
        arquivos_encontrados = leitura_iterativa_com_paralelismo_e_retry(
            repositorio, 
            extensoes_alvo, 
            max_workers=max_workers, 
            max_depth=max_depth
        )
        logger.info(f"Arquivos encontrados para análise '{tipo_analise}': {list(arquivos_encontrados.keys())}")
        return arquivos_encontrados
    except ValueError as e:
        logger.error(f"Erro ao ler arquivos do GitHub para análise '{tipo_analise}': {e}")
        raise
    except RuntimeError as e:
        logger.error(f"Erro de execução ao ler arquivos do GitHub: {e}")
        raise
    except KeyError as e:
        logger.error(f"Erro de chave ao ler arquivos do GitHub: {e}")
        raise
    except TypeError as e:
        logger.error(f"Erro de tipo ao ler arquivos do GitHub: {e}")
        raise

def obter_arquivos_para_analise(repo_nome: str, tipo_analise: str, max_workers: int = None, max_depth: Optional[int] = None):
    """Função principal para obter arquivos para análise com configuração flexível."""
    return ler_arquivos_repositorio_github(repo_nome, tipo_analise, max_workers=max_workers, max_depth=max_depth)
