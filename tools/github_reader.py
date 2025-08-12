import re
from github import Github
from github.Auth import Token
from google.colab import userdata

def conectar_ao_repositorio(repositorio: str) -> object:
    """
    Conecta ao repositório GitHub usando token do Colab.
    """
    github_token = userdata.get('github_token')
    auth = Token(github_token)
    g = Github(auth=auth)
    return g.get_repo(repositorio)

MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}

def deve_ler_arquivo(conteudo, extensoes):
    """
    Decide se o arquivo deve ser lido baseado nas extensões.
    """
    if extensoes is None:
        return True
    return any(conteudo.path.endswith(ext) for ext in extensoes) or conteudo.name in extensoes

def ler_arquivo_conteudo(conteudo):
    """
    Decodifica o conteúdo de um arquivo do GitHub.
    """
    try:
        return conteudo.decoded_content.decode('utf-8')
    except Exception as e:
        # Logging pode ser adicionado aqui
        return None

def leitura_recursiva(repo, extensoes, path="", arquivos_do_repo=None):
    """
    Lê recursivamente arquivos do repositório que correspondam às extensões.
    """
    if arquivos_do_repo is None:
        arquivos_do_repo = {}
    try:
        conteudos = repo.get_contents(path)
        for conteudo in conteudos:
            if conteudo.type == "dir":
                leitura_recursiva(repo, extensoes, conteudo.path, arquivos_do_repo)
            else:
                if deve_ler_arquivo(conteudo, extensoes):
                    codigo = ler_arquivo_conteudo(conteudo)
                    if codigo is not None:
                        arquivos_do_repo[conteudo.path] = codigo
    except Exception as e:
        # Logging pode ser adicionado aqui
        pass
    return arquivos_do_repo

def main(repo, tipo_de_analise: str):
    """
    Função principal para ler arquivos do repositório conforme tipo de análise.
    """
    repositorio_final = conectar_ao_repositorio(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = leitura_recursiva(repositorio_final, extensoes=extensoes_alvo)
    return arquivos_encontrados
