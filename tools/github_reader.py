import re
from github import Github
from github.Auth import Token
from google.colab import userdata
from typing import Dict, Optional

def conectar_ao_repositorio(repositorio: str) -> object:
    """
    Realiza a autenticação e retorna o objeto do repositório GitHub.

    Args:
        repositorio (str): Nome do repositório GitHub.

    Returns:
        object: Objeto de repositório do PyGithub.
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

def filtrar_arquivo_por_extensao(nome_arquivo: str, extensoes: Optional[list]) -> bool:
    """
    Verifica se o arquivo deve ser lido com base em sua extensão ou nome.

    Args:
        nome_arquivo (str): Caminho ou nome do arquivo.
        extensoes (Optional[list]): Lista de extensões ou nomes alvo.

    Returns:
        bool: True se o arquivo deve ser lido, False caso contrário.
    """
    if extensoes is None:
        return True
    return any(nome_arquivo.endswith(ext) for ext in extensoes) or nome_arquivo in extensoes

def leitura_recursiva(repo, extensoes: Optional[list], path: str = "", arquivos_do_repo: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Lê recursivamente arquivos do repositório filtrando por extensões.

    Args:
        repo (object): Objeto de repositório do PyGithub.
        extensoes (Optional[list]): Lista de extensões alvo.
        path (str): Caminho atual na recursão.
        arquivos_do_repo (Optional[Dict[str, str]]): Dicionário acumulador.

    Returns:
        Dict[str, str]: Dicionário com caminhos de arquivos e seus conteúdos.
    """
    if arquivos_do_repo is None:
        arquivos_do_repo = {}
    try:
        conteudos = repo.get_contents(path)
        for conteudo in conteudos:
            if conteudo.type == "dir":
                leitura_recursiva(repo, extensoes, conteudo.path, arquivos_do_repo)
            else:
                if filtrar_arquivo_por_extensao(conteudo.path, extensoes):
                    try:
                        codigo = conteudo.decoded_content.decode('utf-8')
                        arquivos_do_repo[conteudo.path] = codigo
                    except Exception as e:
                        print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")
    except Exception as e:
        print(e)
    return arquivos_do_repo

def main(repo: str, tipo_de_analise: str) -> Dict[str, str]:
    """
    Função principal para leitura de arquivos do repositório conforme tipo de análise.

    Args:
        repo (str): Nome do repositório GitHub.
        tipo_de_analise (str): Tipo de análise (ex: 'python', 'terraform').

    Returns:
        Dict[str, str]: Dicionário com caminhos de arquivos e seus conteúdos.
    """
    repositorio_final = conectar_ao_repositorio(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = leitura_recursiva(repositorio_final, extensoes=extensoes_alvo)
    return arquivos_encontrados
