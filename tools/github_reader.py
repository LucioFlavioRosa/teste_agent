import re
from github import Github
from github.Auth import Token
from google.colab import userdata

def conection(repositorio: str):
    """
    Realiza a conexão autenticada ao repositório GitHub informado.

    Args:
        repositorio (str): Nome do repositório no formato 'usuario/repositorio'.

    Returns:
        github.Repository.Repository: Objeto do repositório GitHub.
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

def _leitura_recursiva_com_debug(repo, extensoes, path="", arquivos_do_repo=None):
    """
    Lê recursivamente arquivos do repositório, filtrando por extensões.

    Args:
        repo (github.Repository.Repository): Objeto do repositório GitHub.
        extensoes (list or None): Lista de extensões de arquivos a filtrar.
        path (str): Caminho relativo dentro do repositório.
        arquivos_do_repo (dict): Dicionário acumulador dos arquivos encontrados.

    Returns:
        dict: Dicionário com caminhos e conteúdos dos arquivos filtrados.
    """
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
                    except Exception as e:
                        print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")
    except Exception as e:
        print(e)
    return arquivos_do_repo

def main(repo, tipo_de_analise: str):
    """
    Função principal que recupera arquivos de um repositório GitHub conforme o tipo de análise.

    Args:
        repo (str): Nome do repositório GitHub.
        tipo_de_analise (str): Tipo de análise ('python', 'terraform', etc.).

    Returns:
        dict: Dicionário com caminhos e conteúdos dos arquivos relevantes.
    """
    repositorio_final = conection(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = _leitura_recursiva_com_debug(repositorio_final,
                                                       extensoes=extensoes_alvo)
    return arquivos_encontrados
