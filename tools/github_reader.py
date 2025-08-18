"""Leitor de código-fonte de repositórios GitHub.

Este módulo fornece funcionalidades para ler e filtrar arquivos de repositórios GitHub
com base em tipos de análise e extensões de arquivo correspondentes.

Dependências:
  - PyGithub: Para interação com a API do GitHub
  - google.colab.userdata: Para obtenção segura do token de autenticação GitHub

O módulo utiliza um mapeamento de tipos de análise para extensões de arquivo relevantes,
permitindo filtrar apenas os arquivos pertinentes para cada tipo de análise.
"""

import re
from github import Github
from github.Auth import Token
from google.colab import userdata

def conection(repositorio: str):
    """Estabelece conexão autenticada com um repositório GitHub.
    
    Utiliza o token armazenado no google.colab.userdata para autenticação
    segura com a API do GitHub, evitando exposição de credenciais no código.
    
    Args:
        repositorio: String com o nome do repositório no formato 'usuario/repo'.
        
    Returns:
        Objeto Repository da PyGithub representando o repositório conectado.
        
    Raises:
        ValueError: Se o token GitHub não estiver disponível no userdata.
        GithubException: Se ocorrer erro de autenticação ou o repositório não existir.
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

    if arquivos_do_repo is None:
        arquivos_do_repo = {}

    try:
        conteudos = repo.get_contents(path)

        for conteudo in conteudos:
            if conteudo.type == "dir":
                _leitura_recursiva_com_debug(repo, extensoes, conteudo.path, arquivos_do_repo)
            else:
                # Determina se o arquivo deve ser lido com base nas extensões ou nome completo
                # Isso permite filtrar tanto por sufixo (.py, .tf) quanto por nome exato (Dockerfile)
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
    """Lê e filtra arquivos de um repositório GitHub com base no tipo de análise.
    
    Conecta-se ao repositório especificado e obtém os arquivos relevantes para
    o tipo de análise solicitado, filtrando por extensões definidas em MAPEAMENTO_TIPO_EXTENSOES.
    
    Args:
        repo: String com o nome do repositório no formato 'usuario/repo'.
        tipo_de_analise: Tipo de análise que determinará quais extensões de arquivo serão filtradas.
        
    Returns:
        Um dicionário mapeando caminhos de arquivo para seus conteúdos em texto.
        Formato: {"caminho/do/arquivo.ext": "conteúdo do arquivo"}
        
    Raises:
        Exception: Se ocorrer erro na conexão ou leitura do repositório.
    """

    repositorio_final = conection(repositorio=repo)

    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())

    arquivos_encontrados = _leitura_recursiva_com_debug(repositorio_final, 
                                                        extensoes=extensoes_alvo)
  
    return arquivos_encontrados