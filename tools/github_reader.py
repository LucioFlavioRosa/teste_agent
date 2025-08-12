import re
from github import Github
from github.Auth import Token
from google.colab import userdata

def conectar_github(repositorio: str):
    """
    Realiza conexão autenticada ao GitHub e retorna o objeto de repositório.
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

def filtrar_extensao(conteudo, extensoes):
    """
    Retorna True se o arquivo deve ser lido, baseado nas extensões.
    """
    if extensoes is None:
        return True
    return any(conteudo.path.endswith(ext) for ext in extensoes) or conteudo.name in extensoes


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
                if filtrar_extensao(conteudo, extensoes):
                    try:
                        codigo = conteudo.decoded_content.decode('utf-8')
                        arquivos_do_repo[conteudo.path] = codigo
                    except Exception as e:
                        print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")
    except Exception as e:
        print(e)
    return arquivos_do_repo


def main(repo, tipo_de_analise: str):
    """
    Função principal de leitura do repositório, mantendo compatibilidade.
    """
    repositorio_final = conectar_github(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = leitura_recursiva(
        repositorio_final,
        extensoes=extensoes_alvo
    )
    return arquivos_encontrados
