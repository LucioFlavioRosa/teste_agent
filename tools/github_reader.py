from github import Github


def obter_codigo_repositorio(repositorio, caminho_credenciais, tipo_analise, extensoes_personalizadas=None):
    """
    Obtém o código do repositório do Github de acordo com o tipo de análise e extensões.
    Args:
        repositorio (str): Endereço do repositório.
        caminho_credenciais (str): Caminho para as credenciais do Github.
        tipo_analise (str): Tipo de análise.
        extensoes_personalizadas (list, opcional): Extensões personalizadas.
    Returns:
        dict: Dicionário com caminhos e conteúdos dos arquivos.
    """
    with open(caminho_credenciais, 'r') as f:
        token = f.read().strip()
    client = Github(token)
    repo = client.get_repo(repositorio)
    extensoes = extensoes_personalizadas if extensoes_personalizadas else [".py"]
    return _leitura_recursiva(repo, '', extensoes)


def _leitura_recursiva(repo, caminho, extensoes):
    """
    Faz a leitura recursiva dos arquivos do repositório, filtrando pelas extensões.
    Args:
        repo (github.Repository.Repository): Objeto do repositório Github.
        caminho (str): Caminho atual.
        extensoes (list): Lista de extensões.
    Returns:
        dict: Dicionário {caminho_do_arquivo: conteudo}
    """
    arquivos = {}
    conteudos = repo.get_contents(caminho)
    for conteudo in conteudos:
        if conteudo.type == 'dir':
            arquivos.update(_leitura_recursiva(repo, conteudo.path, extensoes))
        elif any(conteudo.path.endswith(ext) for ext in extensoes):
            arquivos[conteudo.path] = conteudo.decoded_content.decode('utf-8')
    return arquivos
