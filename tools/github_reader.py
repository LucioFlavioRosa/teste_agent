import re
from github import Github
from github.Auth import Token
from google.colab import userdata

def obter_token_github() -> str:
    """Obtém o token do GitHub do ambiente seguro."""
    return userdata.get('github_token')

def criar_conexao_github(repositorio: str) -> object:
    """Cria e retorna uma conexão autenticada com o repositório GitHub."""
    github_token = obter_token_github()
    auth = Token(github_token)
    g = Github(auth=auth)
    return g.get_repo(repositorio)

MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"]
}

def ler_arquivos_recursivamente(repo, extensoes, path="", arquivos_do_repo=None):
    """
    Lê arquivos recursivamente do repositório conforme as extensões desejadas.
    """
    if arquivos_do_repo is None:
        arquivos_do_repo = {}
    try:
        conteudos = repo.get_contents(path)
        for conteudo in conteudos:
            if conteudo.type == "dir":
                ler_arquivos_recursivamente(repo, extensoes, conteudo.path, arquivos_do_repo)
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
                    except Exception as e:
                        print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")
    except Exception as e:
        print(e)
    return arquivos_do_repo

def main(repo, tipo_de_analise: str):
    """Função principal para leitura de arquivos do repositório a partir do tipo de análise."""
    repositorio_final = criar_conexao_github(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = ler_arquivos_recursivamente(repositorio_final, extensoes=extensoes_alvo)
    return arquivos_encontrados
