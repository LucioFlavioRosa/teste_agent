import os
import logging
from github import Github, Auth
from github.GithubException import GithubException

logger = logging.getLogger(__name__)

def connection(repositorio: str):
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise ValueError("Variável de ambiente GITHUB_TOKEN não definida. Defina GITHUB_TOKEN com um token de acesso do GitHub.")
    auth = Auth.Token(token)
    g = Github(auth=auth)
    return g.get_repo(repositorio)


MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"], 
}

def _leitura_recursiva_com_debug(repo, extensoes, path="", arquivos_do_repo=None):

    if arquivos_do_repo is None:
        arquivos_do_repo = {}

    try:
        conteudos = repo.get_contents(path)
    except GithubException as e:
        logger.error("Falha ao listar conteúdo no repositório %s em '%s': %s", getattr(repo, "full_name", "desconhecido"), path, e)
        raise

    for conteudo in conteudos:
        if conteudo.type == "dir":
            _leitura_recursiva_com_debug(repo, extensoes, conteudo.path, arquivos_do_repo)
        else:
            ler_o_arquivo = False
            if extensoes is None:
                ler_o_arquivo = True
            else:
                if any(conteudo.path.endswith(ext) for ext in extensoes) or conteudo.name in extensoes:
                    ler_o_arquivo = True
                
            if ler_o_arquivo:
                try:
                    codigo = conteudo.decoded_content.decode('utf-8')
                    arquivos_do_repo[conteudo.path] = codigo
                except UnicodeDecodeError as e:
                    logger.warning("Falha ao decodificar arquivo '%s' no caminho '%s': %s", conteudo.name, conteudo.path, e)
                except Exception as e:
                    logger.warning("Erro inesperado ao ler arquivo '%s' no caminho '%s': %s", conteudo.name, conteudo.path, e)
    
    return arquivos_do_repo


def main(repo, tipo_de_analise: str):

    repositorio_final = connection(repositorio=repo)

    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())

    arquivos_encontrados = _leitura_recursiva_com_debug(repositorio_final, 
                                                        extensoes=extensoes_alvo)
  
    return arquivos_encontrados
