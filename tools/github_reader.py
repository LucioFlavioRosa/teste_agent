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
MAX_PARALLELISM_DEFAULT = 4  # Limite padrão
MAX_PARALLELISM_MAX = 16     # Limite máximo permitido


def conectar_ao_github(repositorio_nome: str):
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

def arquivo_esta_na_lista_de_extensoes(arquivo_obj, extensoes_alvo: List[str]):
    if extensoes_alvo is None:
        return True
    if any(arquivo_obj.path.endswith(ext) for ext in extensoes_alvo) or arquivo_obj.name in extensoes_alvo:
        return True
    return False

def ler_conteudo_arquivo_com_retentativas(arquivo_obj):
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


def coletar_arquivos_e_diretorios(conteudos, extensoes_alvo: List[str]):
    arquivos = []
    diretorios = []
    for item in conteudos:
        if item.type == "dir":
            diretorios.append(item.path)
        else:
            if arquivo_esta_na_lista_de_extensoes(item, extensoes_alvo):
                arquivos.append(item)
    return arquivos, diretorios


def ajustar_paralelismo_dinamico(qtd_arquivos: int) -> int:
    if qtd_arquivos < 10:
        return MAX_PARALLELISM_DEFAULT
    elif qtd_arquivos < 50:
        return min(MAX_PARALLELISM_DEFAULT * 2, MAX_PARALLELISM_MAX)
    else:
        return MAX_PARALLELISM_MAX


def ler_arquivos_de_diretorio(repo, caminho, extensoes_alvo, max_workers, profundidade_atual, max_depth):
    arquivos_do_repo = {}
    try:
        conteudos = repo.get_contents(caminho)
    except Exception as e:
        logging.error(f"Erro ao obter conteúdo em '{caminho}': {type(e).__name__}: {e}")
        return arquivos_do_repo, []
    arquivos, diretorios = coletar_arquivos_e_diretorios(conteudos, extensoes_alvo)
    max_workers_ajustado = ajustar_paralelismo_dinamico(len(arquivos))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers_ajustado) as executor:
        futuros = {executor.submit(ler_conteudo_arquivo_com_retentativas, arquivo): arquivo for arquivo in arquivos}
        for futuro in concurrent.futures.as_completed(futuros):
            arquivo = futuros[futuro]
            conteudo = futuro.result()
            if conteudo is not None:
                arquivos_do_repo[arquivo.path] = conteudo
    # Limitação de profundidade
    if max_depth is not None and profundidade_atual >= max_depth:
        return arquivos_do_repo, []
    return arquivos_do_repo, diretorios


def leitura_modularizada_com_paralelismo_e_limite(repo, extensoes_alvo: List[str], caminho_inicial="", max_workers=MAX_PARALLELISM_DEFAULT, max_depth: Optional[int]=None):
    """
    Percorre o repositório de forma iterativa, modularizada e paraleliza leitura de arquivos e diretórios.
    Implementa retry para leitura de arquivos, ajuste dinâmico de paralelismo e limita profundidade.
    """
    arquivos_do_repo = {}
    caminhos_a_explorar = [(caminho_inicial, 0)]
    while caminhos_a_explorar:
        caminho_atual, profundidade = caminhos_a_explorar.pop()
        arquivos_lidos, diretorios = ler_arquivos_de_diretorio(
            repo, caminho_atual, extensoes_alvo, max_workers, profundidade, max_depth
        )
        arquivos_do_repo.update(arquivos_lidos)
        caminhos_a_explorar.extend([(d, profundidade + 1) for d in diretorios])
    return arquivos_do_repo


def ler_arquivos_repositorio_github(repositorio_nome: str, tipo_analise: str, max_workers: int = MAX_PARALLELISM_DEFAULT, max_depth: Optional[int] = None):
    try:
        repositorio = conectar_ao_github(repositorio_nome=repositorio_nome)
        extensoes_alvo = TIPO_EXTENSOES_MAPEAMENTO.get(tipo_analise.lower())
        arquivos_encontrados = leitura_modularizada_com_paralelismo_e_limite(repositorio, extensoes_alvo, max_workers=max_workers, max_depth=max_depth)
        logging.info(f"Arquivos encontrados para análise '{tipo_analise}': {list(arquivos_encontrados.keys())}")
        return arquivos_encontrados
    except Exception as e:
        logging.error(f"Erro ao ler arquivos do GitHub para análise '{tipo_analise}': {e}")
        raise


def obter_arquivos_para_analise(repo_nome: str, tipo_analise: str, max_workers: int = MAX_PARALLELISM_DEFAULT, max_depth: Optional[int] = None):
    return ler_arquivos_repositorio_github(repo_nome, tipo_analise, max_workers=max_workers, max_depth=max_depth)
