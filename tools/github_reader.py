import re
from github import Github
from github.Auth import Token
from google.colab import userdata
import logging
import concurrent.futures

# Configuração básica de logging estruturado
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"], 
}

def conectar_ao_github(repositorio: str):
    """
    Realiza conexão autenticada ao GitHub e retorna o objeto de repositório.
    """
    try:
        GITHUB_TOKEN = userdata.get('github_token')
        if not GITHUB_TOKEN:
            logging.error("Token do GitHub não encontrado em userdata.")
            raise ValueError("Token do GitHub não encontrado.")
        auth = Token(GITHUB_TOKEN)
        g = Github(auth=auth)
        repo_obj = g.get_repo(repositorio)
        logging.info(f"Conexão bem-sucedida com o repositório: {repositorio}")
        return repo_obj
    except Exception as e:
        logging.exception(f"Erro ao conectar ao GitHub para o repositório '{repositorio}': {e}")
        raise

def deve_ler_arquivo(conteudo, extensoes):
    """
    Decide se um arquivo deve ser lido com base nas extensões alvo.
    """
    if extensoes is None:
        return True
    if any(conteudo.path.endswith(ext) for ext in extensoes) or conteudo.name in extensoes:
        return True
    return False

def ler_arquivo_do_github(conteudo):
    """
    Lê e decodifica o conteúdo de um arquivo do GitHub.
    """
    try:
        codigo = conteudo.decoded_content.decode('utf-8')
        return codigo
    except Exception as e:
        logging.exception(f"Erro na decodificação de '{conteudo.path}': {e}")
        return None

def leitura_recursiva(repo, extensoes, path="", arquivos_do_repo=None, max_workers=8):
    """
    Função recursiva para percorrer diretórios e ler arquivos do repositório GitHub.
    Agora utiliza paralelização para leitura dos arquivos.
    """
    if arquivos_do_repo is None:
        arquivos_do_repo = {}
    try:
        conteudos = repo.get_contents(path)
        arquivos = []
        diretorios = []
        for conteudo in conteudos:
            if conteudo.type == "dir":
                diretorios.append(conteudo.path)
            else:
                if deve_ler_arquivo(conteudo, extensoes):
                    arquivos.append(conteudo)
        # Paraleliza leitura dos arquivos elegíveis
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futuros = {executor.submit(ler_arquivo_do_github, arquivo): arquivo for arquivo in arquivos}
            for futuro in concurrent.futures.as_completed(futuros):
                arquivo = futuros[futuro]
                codigo = futuro.result()
                if codigo is not None:
                    arquivos_do_repo[arquivo.path] = codigo
        # Processa diretórios recursivamente
        for dir_path in diretorios:
            leitura_recursiva(repo, extensoes, dir_path, arquivos_do_repo, max_workers)
    except Exception as e:
        logging.exception(f"Erro ao ler arquivos em '{path}': {e}")
    return arquivos_do_repo

def ler_arquivos_do_github(repo, tipo_de_analise: str):
    """
    Função principal para ler arquivos do GitHub conforme o tipo de análise.
    """
    try:
        repositorio_final = conectar_ao_github(repositorio=repo)
        extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
        arquivos_encontrados = leitura_recursiva(repositorio_final, extensoes=extensoes_alvo)
        logging.info(f"Arquivos encontrados para análise '{tipo_de_analise}': {list(arquivos_encontrados.keys())}")
        return arquivos_encontrados
    except Exception as e:
        logging.exception(f"Erro na leitura dos arquivos do GitHub para análise '{tipo_de_analise}': {e}")
        raise

def main(repo: str, tipo_de_analise: str):
    return ler_arquivos_do_github(repo, tipo_de_analise)