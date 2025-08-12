import re
from github import Github
from github.Auth import Token
from google.colab import userdata
from typing import Dict, Optional

def obter_token_github() -> str:
    """Obtém o token do GitHub do ambiente Colab."""
    return userdata.get('github_token')

def criar_conexao_github(repositorio: str, token: Optional[str] = None):
    """Cria uma conexão autenticada com o GitHub usando o token fornecido."""
    if token is None:
        token = obter_token_github()
    auth = Token(token)
    g = Github(auth=auth)
    return g.get_repo(repositorio)

MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}

def filtrar_extensao_arquivo(conteudo, extensoes) -> bool:
    """Determina se o arquivo deve ser lido com base na extensão."""
    if extensoes is None:
        return True
    return any(conteudo.path.endswith(ext) for ext in extensoes) or conteudo.name in extensoes

def ler_arquivo_repo(conteudo) -> Optional[str]:
    """Tenta decodificar o conteúdo do arquivo."""
    try:
        return conteudo.decoded_content.decode('utf-8')
    except Exception as e:
        print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")
        return None

def leitura_recursiva(repo, extensoes, path="", arquivos_do_repo=None) -> Dict[str, str]:
    """Lê recursivamente arquivos do repositório, filtrando por extensão."""
    if arquivos_do_repo is None:
        arquivos_do_repo = {}
    try:
        conteudos = repo.get_contents(path)
        for conteudo in conteudos:
            if conteudo.type == "dir":
                leitura_recursiva(repo, extensoes, conteudo.path, arquivos_do_repo)
            else:
                if filtrar_extensao_arquivo(conteudo, extensoes):
                    codigo = ler_arquivo_repo(conteudo)
                    if codigo is not None:
                        arquivos_do_repo[conteudo.path] = codigo
    except Exception as e:
        print(e)
    return arquivos_do_repo

def main(repo, tipo_de_analise: str, token: Optional[str] = None) -> Dict[str, str]:
    """Função principal para obter arquivos do repositório conforme o tipo de análise."""
    repositorio_final = criar_conexao_github(repositorio=repo, token=token)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = leitura_recursiva(
        repositorio_final,
        extensoes=extensoes_alvo
    )
    return arquivos_encontrados
