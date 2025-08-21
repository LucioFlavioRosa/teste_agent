import re
from github import Github
from github.Auth import Token
from google.colab import userdata
import logging
import concurrent.futures
from typing import Dict, Any, List

# Configuração básica de logging estruturado
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

TIPO_EXTENSOES_MAPEAMENTO = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}

def conectar_ao_github(repositorio_nome: str):
    """
    Realiza conexão autenticada ao GitHub e retorna o objeto de repositório.
    """
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
    except Exception as e:
        logging.exception(f"Erro inesperado ao conectar ao GitHub para o repositório '{repositorio_nome}': {e}")
        raise

def arquivo_deve_ser_lido(arquivo_obj, extensoes_alvo: List[str]):
    """
    Decide se um arquivo deve ser lido com base nas extensões alvo.
    """
    if extensoes_alvo is None:
        return True
    if any(arquivo_obj.path.endswith(ext) for ext in extensoes_alvo) or arquivo_obj.name in extensoes_alvo:
        return True
    return False

def ler_conteudo_arquivo_github(arquivo_obj):
    """
    Lê e decodifica o conteúdo de um arquivo do GitHub.
    """
    try:
        conteudo_arquivo = arquivo_obj.decoded_content.decode('utf-8')
        return conteudo_arquivo
    except AttributeError as e:
        logging.error(f"Arquivo sem conteúdo decodificável '{arquivo_obj.path}': {e}")
        return None
    except Exception as e:
        logging.error(f"Erro inesperado na decodificação de '{arquivo_obj.path}': {e}")
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

def leitura_iterativa_com_paralelismo(repo, extensoes_alvo: List[str], caminho_inicial="", max_workers=8):
    """
    Percorre o repositório de forma iterativa (não recursiva) e paraleliza leitura de arquivos e diretórios.
    """
    arquivos_do_repo = {}
    caminhos_a_explorar = [caminho_inicial]
    while caminhos_a_explorar:
        caminho_atual = caminhos_a_explorar.pop()
        try:
            conteudos = repo.get_contents(caminho_atual)
        except Exception as e:
            logging.error(f"Erro ao obter conteúdo em '{caminho_atual}': {e}")
            continue
        arquivos, diretorios = coletar_arquivos_e_diretorios(conteudos, extensoes_alvo)
        # Paraleliza leitura dos arquivos elegíveis
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futuros = {executor.submit(ler_conteudo_arquivo_github, arquivo): arquivo for arquivo in arquivos}
            for futuro in concurrent.futures.as_completed(futuros):
                arquivo = futuros[futuro]
                conteudo = futuro.result()
                if conteudo is not None:
                    arquivos_do_repo[arquivo.path] = conteudo
        # Adiciona diretórios para próxima iteração
        caminhos_a_explorar.extend(diretorios)
    return arquivos_do_repo

def ler_arquivos_repositorio_github(repositorio_nome: str, tipo_analise: str):
    """
    Função principal para ler arquivos do GitHub conforme o tipo de análise.
    """
    try:
        repositorio = conectar_ao_github(repositorio_nome=repositorio_nome)
        extensoes_alvo = TIPO_EXTENSOES_MAPEAMENTO.get(tipo_analise.lower())
        arquivos_encontrados = leitura_iterativa_com_paralelismo(repositorio, extensoes_alvo)
        logging.info(f"Arquivos encontrados para análise '{tipo_analise}': {list(arquivos_encontrados.keys())}")
        return arquivos_encontrados
    except (ValueError, RuntimeError) as e:
        logging.error(f"Erro ao ler arquivos do GitHub para análise '{tipo_analise}': {e}")
        raise
    except Exception as e:
        logging.error(f"Erro inesperado na leitura dos arquivos do GitHub para análise '{tipo_analise}': {e}")
        raise

def obter_arquivos_para_analise(repo_nome: str, tipo_analise: str):
    return ler_arquivos_repositorio_github(repo_nome, tipo_analise)
