import re
from github import Github
from github.Auth import Token
from google.colab import userdata

MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}

def conection(repositorio: str):
    """
    Realiza a conexão com o repositório GitHub usando token do Colab.
    Args:
        repositorio (str): Nome do repositório.
    Returns:
        github.Repository.Repository: Objeto de repositório.
    """
    GITHUB_TOKEN = userdata.get('github_token')
    auth = Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    return g.get_repo(repositorio)


def _deve_ler_arquivo(conteudo, extensoes) -> bool:
    """
    Decide se o arquivo deve ser lido com base nas extensões.
    """
    if extensoes is None:
        return True
    if any(conteudo.path.endswith(ext) for ext in extensoes):
        return True
    if conteudo.name in extensoes:
        return True
    return False


def _leitura_recursiva(repo, extensoes, path="", arquivos_do_repo=None):
    """
    Lê recursivamente arquivos do repositório, filtrando por extensão.
    Args:
        repo: Objeto de repositório GitHub.
        extensoes (list): Lista de extensões alvo.
        path (str): Caminho atual.
        arquivos_do_repo (dict): Dicionário acumulador.
    Returns:
        dict: Arquivos lidos.
    """
    if arquivos_do_repo is None:
        arquivos_do_repo = {}
    try:
        conteudos = repo.get_contents(path)
        for conteudo in conteudos:
            if conteudo.type == "dir":
                _leitura_recursiva(repo, extensoes, conteudo.path, arquivos_do_repo)
            else:
                if _deve_ler_arquivo(conteudo, extensoes):
                    try:
                        codigo = conteudo.decoded_content.decode('utf-8')
                        arquivos_do_repo[conteudo.path] = codigo
                    except Exception as exc:
                        # Logging pode ser adicionado aqui se necessário
                        pass
    except Exception as exc:
        # Logging pode ser adicionado aqui se necessário
        pass
    return arquivos_do_repo


def main(repo, tipo_de_analise: str, leitura_recursiva_func=_leitura_recursiva, conection_func=conection):
    """
    Função principal para leitura de arquivos do repositório.
    Args:
        repo (str): Nome do repositório.
        tipo_de_analise (str): Tipo de análise.
        leitura_recursiva_func (callable): Função de leitura recursiva.
        conection_func (callable): Função de conexão com o GitHub.
    Returns:
        dict: Arquivos encontrados.
    """
    repositorio_final = conection_func(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = leitura_recursiva_func(
        repositorio_final,
        extensoes=extensoes_alvo
    )
    return arquivos_encontrados
