import re
from github import Github
from github.Auth import Token
from google.colab import userdata


def obter_conexao_github(repositorio: str):
    """
    Obtém conexão autenticada com o repositório do GitHub.
    """
    GITHUB_TOKEN = userdata.get('github_token')
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


def deve_ler_arquivo(conteudo, extensoes):
    """
    Decide se o arquivo deve ser lido com base nas extensões alvo.
    """
    if extensoes is None:
        return True
    if any(conteudo.path.endswith(ext) for ext in extensoes) or conteudo.name in extensoes:
        return True
    return False


def ler_arquivo_do_github(conteudo):
    """
    Decodifica o conteúdo de um arquivo do GitHub.
    """
    try:
        return conteudo.decoded_content.decode('utf-8')
    except Exception as e:
        print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")
        return None


def leitura_recursiva(repo, extensoes, path="", arquivos_do_repo=None):
    """
    Realiza leitura recursiva dos arquivos do repositório, filtrando por extensão.
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
                    codigo = ler_arquivo_do_github(conteudo)
                    if codigo is not None:
                        arquivos_do_repo[conteudo.path] = codigo
    except Exception as e:
        print(e)
    return arquivos_do_repo


def main(repo, tipo_de_analise: str):
    """
    Função principal para extração de código do repositório.
    """
    repositorio_final = obter_conexao_github(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = leitura_recursiva(
        repositorio_final,
        extensoes=extensoes_alvo
    )
    return arquivos_encontrados
