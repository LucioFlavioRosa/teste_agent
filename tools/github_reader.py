import re
from github import Github
from github.Auth import Token
from google.colab import userdata
import logging
import concurrent.futures
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

TIPO_EXTENSOES_MAPEAMENTO = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}

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
    except (ValueError, RuntimeError) as e:
        logging.error(f"Erro ao conectar ao GitHub para o repositório '{repositorio_nome}': {e}")
        raise
    except KeyError as e:
        logging.error(f"Erro de chave ao conectar ao GitHub: {e}")
        raise
    except TypeError as e:
        logging.error(f"Erro de tipo ao conectar ao GitHub: {e}")
        raise

def arquivo_deve_ser_lido(arquivo_obj, extensoes_alvo: List[str]):
    if extensoes_alvo is None:
        return True
    if any(arquivo_obj.path.endswith(ext) for ext in extensoes_alvo) or arquivo_obj.name in extensoes_alvo:
        return True
    return False

def ler_conteudo_arquivo_github(arquivo_obj):
    try:
        conteudo_arquivo = arquivo_obj.decoded_content.decode('utf-8')
        return conteudo_arquivo
    except AttributeError as e:
        logging.error(f"Arquivo sem conteúdo decodificável '{arquivo_obj.path}': {e}")
        return None
    except Exception as e:
        logging.error(f"Erro inesperado na decodificação de '{arquivo_obj.path}': {type(e).__name__}: {e}")
        return None

def coletar_arquivos_e_diretorios(conteudos, extensoes_alvo: List[str]):
    arquivos = []
    diretorios = []
    for item in conteudos:
        if item.type == "dir":
            diretorios.append(item.path)
        else:
            if arquivo_deve_ser_lido(item, extensoes_alvo):
                arquivos.append(item)
    return arquivos, diretorios

def leitura_iterativa_com_paralelismo(repo, extensoes_alvo: List[str], caminho_inicial="", max_workers=8, max_depth: Optional[int]=None):
    """
    Percorre o repositório de forma iterativa e paraleliza leitura de arquivos e diretórios.
    Permite configurar número de workers e profundidade máxima de diretórios.
    """
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
        arquivos, diretorios = coletar_arquivos_e_diretorios(conteudos, extensoes_alvo)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futuros = {executor.submit(ler_conteudo_arquivo_github, arquivo): arquivo for arquivo in arquivos}
            for futuro in concurrent.futures.as_completed(futuros):
                arquivo = futuros[futuro]
                conteudo = futuro.result()
                if conteudo is not None:
                    arquivos_do_repo[arquivo.path] = conteudo
        caminhos_a_explorar.extend([(d, profundidade + 1) for d in diretorios])
    return arquivos_do_repo

def ler_arquivos_repositorio_github(repositorio_nome: str, tipo_analise: str, max_workers: int = 8, max_depth: Optional[int] = None):
    try:
        repositorio = conectar_ao_github(repositorio_nome=repositorio_nome)
        extensoes_alvo = TIPO_EXTENSOES_MAPEAMENTO.get(tipo_analise.lower())
        arquivos_encontrados = leitura_iterativa_com_paralelismo(repositorio, extensoes_alvo, max_workers=max_workers, max_depth=max_depth)
        logging.info(f"Arquivos encontrados para análise '{tipo_analise}': {list(arquivos_encontrados.keys())}")
        return arquivos_encontrados
    except (ValueError, RuntimeError) as e:
        logging.error(f"Erro ao ler arquivos do GitHub para análise '{tipo_analise}': {e}")
        raise
    except KeyError as e:
        logging.error(f"Erro de chave ao ler arquivos do GitHub: {e}")
        raise
    except TypeError as e:
        logging.error(f"Erro de tipo ao ler arquivos do GitHub: {e}")
        raise

def obter_arquivos_para_analise(repo_nome: str, tipo_analise: str, max_workers: int = 8, max_depth: Optional[int] = None):
    return ler_arquivos_repositorio_github(repo_nome, tipo_analise, max_workers=max_workers, max_depth=max_depth)
