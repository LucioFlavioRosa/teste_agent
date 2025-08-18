import logging
from github import Github
from github.Auth import Token
from tools.segredos import get_secret

def connect_repo(repositorio: str):
    """Conecta ao repositório GitHub usando token de ambiente ou Colab."""
    GITHUB_TOKEN = get_secret('GITHUB_TOKEN')
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN não encontrado em variáveis de ambiente ou Colab userdata.")
    auth = Token(GITHUB_TOKEN)
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
                        logging.info(f"Arquivo lido: {conteudo.path} (tamanho: {len(codigo)} bytes)")
                    except Exception as e:
                        logging.error(f"ERRO na decodificação de '{conteudo.path}': {e}")
                        raise  # Propaga exceção crítica
    except Exception as e:
        logging.error(f"Erro ao ler o caminho '{path}': {e}")
        raise
    return arquivos_do_repo

def main(repo, tipo_de_analise: str):
    repositorio_final = connect_repo(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = _leitura_recursiva_com_debug(repositorio_final, 
                                                        extensoes=extensoes_alvo)
    return arquivos_encontrados
