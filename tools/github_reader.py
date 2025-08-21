import re
from github import Github
from github.Auth import Token
from google.colab import userdata
import logging
import concurrent.futures
from typing import Dict, Any, List, Optional
import time

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


def conectar_ao_github(nome_repositorio: str):
    try:
        GITHUB_TOKEN = userdata.get('github_token')
        if not GITHUB_TOKEN:
            logging.error("Token do GitHub não encontrado em userdata.")
            raise ValueError("Token do GitHub não encontrado.")
        auth = Token(GITHUB_TOKEN)
        github_client = Github(auth=auth)
        repositorio = github_client.get_repo(nome_repositorio)
        logging.info(f"Conexão bem-sucedida com o repositório: {nome_repositorio}")
        return repositorio
    except ValueError as erro:
        logging.error(f"Erro ao conectar ao GitHub para o repositório '{nome_repositorio}': {erro}")
        raise
    except RuntimeError as erro:
        logging.error(f"Erro de execução ao conectar ao GitHub: {erro}")
        raise
    except KeyError as erro:
        logging.error(f"Erro de chave ao conectar ao GitHub: {erro}")
        raise
    except TypeError as erro:
        logging.error(f"Erro de tipo ao conectar ao GitHub: {erro}")
        raise


def arquivo_possui_extensao_valida(arquivo_objeto, extensoes_permitidas: List[str]):
    if extensoes_permitidas is None:
        return True
    if any(arquivo_objeto.path.endswith(ext) for ext in extensoes_permitidas) or arquivo_objeto.name in extensoes_permitidas:
        return True
    return False


def ler_conteudo_arquivo_com_retentativas(arquivo_objeto):
    for tentativa in range(1, MAX_RETRIES + 1):
        try:
            conteudo_arquivo = arquivo_objeto.decoded_content.decode('utf-8')
            return conteudo_arquivo
        except AttributeError as erro:
            logging.error(f"Arquivo sem conteúdo decodificável '{arquivo_objeto.path}': {erro}")
            return None
        except Exception as erro:
            logging.error(f"Erro inesperado na decodificação de '{arquivo_objeto.path}' (tentativa {tentativa}/{MAX_RETRIES}): {type(erro).__name__}: {erro}")
            if tentativa < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                return None


def coletar_arquivos_e_diretorios(conteudos_diretorio, extensoes_permitidas: List[str]):
    arquivos = []
    diretorios = []
    for conteudo in conteudos_diretorio:
        if conteudo.type == "dir":
            diretorios.append(conteudo.path)
        else:
            if arquivo_possui_extensao_valida(conteudo, extensoes_permitidas):
                arquivos.append(conteudo)
    return arquivos, diretorios


def monitorar_e_ajustar_paralelismo(qtd_arquivos: int) -> int:
    """
    Ajusta dinamicamente o paralelismo para evitar throttling da API do GitHub.
    """
    if qtd_arquivos > 100:
        return max(1, MAX_PARALLELISM // 2)
    return MAX_PARALLELISM


def ler_arquivos_em_diretorios(repo, extensoes_permitidas: List[str], caminho_inicial="", max_workers=MAX_PARALLELISM, profundidade_maxima: Optional[int]=None):
    """
    Percorre o repositório de forma iterativa e paraleliza leitura de arquivos e diretórios.
    Implementa retry para leitura de arquivos e limita paralelismo conforme limites da API.
    Função dividida para melhor clareza e responsabilidade única.
    """
    arquivos_do_repositorio = {}
    caminhos_a_explorar = [(caminho_inicial, 0)]
    while caminhos_a_explorar:
        caminho_atual, nivel_profundidade = caminhos_a_explorar.pop()
        if profundidade_maxima is not None and nivel_profundidade > profundidade_maxima:
            continue
        try:
            conteudos_diretorio = repo.get_contents(caminho_atual)
        except Exception as erro:
            logging.error(f"Erro ao obter conteúdo em '{caminho_atual}': {type(erro).__name__}: {erro}")
            continue
        arquivos, diretorios = coletar_arquivos_e_diretorios(conteudos_diretorio, extensoes_permitidas)
        workers_ajustados = monitorar_e_ajustar_paralelismo(len(arquivos))
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers_ajustados) as executor:
            futuros = {executor.submit(ler_conteudo_arquivo_com_retentativas, arquivo): arquivo for arquivo in arquivos}
            for futuro in concurrent.futures.as_completed(futuros):
                arquivo = futuros[futuro]
                conteudo = futuro.result()
                if conteudo is not None:
                    arquivos_do_repositorio[arquivo.path] = conteudo
        caminhos_a_explorar.extend([(diretorio, nivel_profundidade + 1) for diretorio in diretorios])
    return arquivos_do_repositorio


def ler_arquivos_repositorio_github(nome_repositorio: str, tipo_analise: str, max_workers: int = MAX_PARALLELISM, profundidade_maxima: Optional[int] = None):
    try:
        repositorio = conectar_ao_github(nome_repositorio=nome_repositorio)
        extensoes_permitidas = TIPO_EXTENSOES_MAPEAMENTO.get(tipo_analise.lower())
        if profundidade_maxima is None:
            raise ValueError("O parâmetro 'profundidade_maxima' é obrigatório para evitar sobrecarga em repositórios grandes.")
        arquivos_encontrados = ler_arquivos_em_diretorios(repositorio, extensoes_permitidas, max_workers=max_workers, profundidade_maxima=profundidade_maxima)
        logging.info(f"Arquivos encontrados para análise '{tipo_analise}': {list(arquivos_encontrados.keys())}")
        return arquivos_encontrados
    except ValueError as erro:
        logging.error(f"Erro ao ler arquivos do GitHub para análise '{tipo_analise}': {erro}")
        raise
    except RuntimeError as erro:
        logging.error(f"Erro de execução ao ler arquivos do GitHub: {erro}")
        raise
    except KeyError as erro:
        logging.error(f"Erro de chave ao ler arquivos do GitHub: {erro}")
        raise
    except TypeError as erro:
        logging.error(f"Erro de tipo ao ler arquivos do GitHub: {erro}")
        raise
    except Exception as erro:
        logging.error(f"Erro inesperado ao ler arquivos do GitHub: {type(erro).__name__}: {erro}")
        raise


def obter_arquivos_para_analise(repo_nome: str, tipo_analise: str, max_workers: int = MAX_PARALLELISM, profundidade_maxima: Optional[int] = None):
    return ler_arquivos_repositorio_github(repo_nome, tipo_analise, max_workers=max_workers, profundidade_maxima=profundidade_maxima)
