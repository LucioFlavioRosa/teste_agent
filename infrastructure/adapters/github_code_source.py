from domain/interfaces/code_source_interface import ICodeSource
from domain/strategies/file_filter_strategy import IFileFilterStrategy
from github import Github
from github.Auth import Token
from google.colab import userdata
import logging
import concurrent.futures
import time

class GitHubCodeSource(ICodeSource):
    def __init__(self, file_filter_strategy: IFileFilterStrategy):
        self.file_filter_strategy = file_filter_strategy
        self.max_retries = 3
        self.retry_delay = 2
        self.max_parallelism = 4

    def conectar_ao_github(self, repositorio_nome):
        GITHUB_TOKEN = userdata.get('github_token')
        if not GITHUB_TOKEN:
            logging.error("Token do GitHub não encontrado em userdata.")
            raise ValueError("Token do GitHub não encontrado.")
        auth = Token(GITHUB_TOKEN)
        github_client = Github(auth=auth)
        repositorio = github_client.get_repo(repositorio_nome)
        return repositorio

    def ler_conteudo_arquivo_com_retry(self, arquivo_obj):
        for tentativa in range(1, self.max_retries + 1):
            try:
                conteudo_arquivo = arquivo_obj.decoded_content.decode('utf-8')
                return conteudo_arquivo
            except Exception:
                if tentativa < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    return None

    def coletar_arquivos_e_diretorios(self, conteudos):
        arquivos = []
        diretorios = []
        for item in conteudos:
            if item.type == "dir":
                diretorios.append(item.path)
            else:
                if self.file_filter_strategy.filtrar(item):
                    arquivos.append(item)
        return arquivos, diretorios

    def leitura_iterativa_com_paralelismo_e_retry(self, repo, caminho_inicial="", max_depth=None):
        arquivos_do_repo = {}
        caminhos_a_explorar = [(caminho_inicial, 0)]
        while caminhos_a_explorar:
            caminho_atual, profundidade = caminhos_a_explorar.pop()
            if max_depth is not None and profundidade > max_depth:
                continue
            try:
                conteudos = repo.get_contents(caminho_atual)
            except Exception:
                continue
            arquivos, diretorios = self.coletar_arquivos_e_diretorios(conteudos)
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_parallelism) as executor:
                futuros = {executor.submit(self.ler_conteudo_arquivo_com_retry, arquivo): arquivo for arquivo in arquivos}
                for futuro in concurrent.futures.as_completed(futuros):
                    arquivo = futuros[futuro]
                    conteudo = futuro.result()
                    if conteudo is not None:
                        arquivos_do_repo[arquivo.path] = conteudo
            caminhos_a_explorar.extend([(d, profundidade + 1) for d in diretorios])
        return arquivos_do_repo

    def obter_codigo(self, repositorio: str, tipo_analise: str):
        repo = self.conectar_ao_github(repositorio)
        return self.leitura_iterativa_com_paralelismo_e_retry(repo)