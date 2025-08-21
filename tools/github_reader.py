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
MAX_PARALLELISM_PADRAO = 4  # Limite padrão para evitar throttling da API
THROTTLE_DELAY = 1  # segundos entre chamadas para controle de taxa


def conectar_github_repositorio(repositorio_nome: str):
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
        logging.error(f"Erro ao conectar ao GitHub para o repositório '{repositorio_nome}': {type(e).__name__}: {e}")
        raise


def arquivo_possui_extensao_alvo(arquivo_obj, extensoes_alvo: List[str]):
    if extensoes_alvo is None:
        return True
    if any(arquivo_obj.path.endswith(ext) for ext in extensoes_alvo) or arquivo_obj.name in extensoes_alvo:
        return True
    return False


def ler_arquivo_com_retentativas(arquivo_obj):
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


def filtrar_arquivos_e_diretorios(conteudos, extensoes_alvo: List[str]):
    arquivos = []
    diretorios = []
    for item in conteudos:
        if item.type == "dir":
            diretorios.append(item.path)
        else:
            if arquivo_possui_extensao_alvo(item, extensoes_alvo):
                arquivos.append(item)
    return arquivos, diretorios


def obter_max_paralelismo():
    # Pode ser ajustado dinamicamente conforme tamanho do repositório ou limites da API
    return MAX_PARALLELISM_PADRAO


def controle_de_taxa():
    time.sleep(THROTTLE_DELAY)


def explorar_repositorio_iterativo(repo, extensoes_alvo: List[str], caminho_inicial="", max_workers=None, max_depth: Optional[int]=None):
    """
    Percorre o repositório de forma iterativa e paraleliza leitura de arquivos e diretórios.
    Implementa retry para leitura de arquivos e limita paralelismo conforme limites da API.
    Adiciona controle de taxa entre chamadas para evitar throttling.
    """
    arquivos_do_repo = {}
    caminhos_a_explorar = [(caminho_inicial, 0)]
    max_workers = max_workers if max_workers is not None else obter_max_paralelismo()
    while caminhos_a_explorar:
        caminho_atual, profundidade = caminhos_a_explorar.pop()
        if max_depth is not None and profundidade > max_depth:
            continue
        try:
            controle_de_taxa()
            conteudos = repo.get_contents(caminho_atual)
        except Exception as e:
            logging.error(f"Erro ao obter conteúdo em '{caminho_atual}': {type(e).__name__}: {e}")
            continue
        arquivos, diretorios = filtrar_arquivos_e_diretorios(conteudos, extensoes_alvo)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futuros = {executor.submit(ler_arquivo_com_retentativas, arquivo): arquivo for arquivo in arquivos}
            for futuro in concurrent.futures.as_completed(futuros):
                arquivo = futuros[futuro]
                conteudo = futuro.result()
                if conteudo is not None:
                    arquivos_do_repo[arquivo.path] = conteudo
        caminhos_a_explorar.extend([(d, profundidade + 1) for d in diretorios])
    return arquivos_do_repo


def coletar_arquivos_repositorio_github(repositorio_nome: str, tipo_analise: str, max_workers: int = None, max_depth: Optional[int] = None):
    try:
        repositorio = conectar_github_repositorio(repositorio_nome=repositorio_nome)
        extensoes_alvo = TIPO_EXTENSOES_MAPEAMENTO.get(tipo_analise.lower())
        arquivos_encontrados = explorar_repositorio_iterativo(repositorio, extensoes_alvo, max_workers=max_workers, max_depth=max_depth)
        logging.info(f"Arquivos encontrados para análise '{tipo_analise}': {list(arquivos_encontrados.keys())}")
        return arquivos_encontrados
    except Exception as e:
        logging.error(f"Erro ao ler arquivos do GitHub para análise '{tipo_analise}': {e}")
        raise


def coletar_arquivos_para_analise(repo_nome: str, tipo_analise: str, max_workers: int = None, max_depth: Optional[int] = None):
    return coletar_arquivos_repositorio_github(repo_nome, tipo_analise, max_workers=max_workers, max_depth=max_depth)
