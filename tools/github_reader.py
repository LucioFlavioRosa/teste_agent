import os
from github import Github

MAPEAMENTO_TIPO_EXTENSOES = {
    'design': ['.py', '.js', '.ts', '.java', '.cs', '.go'],
    'pentest': ['.py', '.js', '.ts', '.java', '.cs', '.go'],
    'documentacao': ['.md', '.rst', '.txt'],
}

def ler_arquivos_do_repositorio(repositorio, tipo_analise, token_github):
    """
    Lê arquivos do repositório filtrando pelas extensões do tipo de análise.

    Args:
        repositorio (str): URL do repositório.
        tipo_analise (str): Tipo de análise para filtrar extensões.
        token_github (str): Token de autenticação do Github.

    Returns:
        dict: Dicionário com caminhos e conteúdos dos arquivos lidos.
    """
    github = Github(token_github)
    repo = github.get_repo(repositorio)
    extensoes = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_analise, [])
    arquivos = {}
    _leitura_recursiva(repo.get_contents(""), extensoes, arquivos)
    return arquivos


def _leitura_recursiva(conteudo, extensoes, arquivos):
    """
    Função recursiva para percorrer diretórios e coletar arquivos.
    """
    for item in conteudo:
        if item.type == 'dir':
            _leitura_recursiva(item.repo.get_contents(item.path), extensoes, arquivos)
        else:
            if any(item.path.endswith(ext) for ext in extensoes):
                arquivos[item.path] = item.decoded_content.decode('utf-8')
