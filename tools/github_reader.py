import os
from github import Github
from github.Auth import Token
from typing import Optional, Dict, Any, List


def conection(repositorio: str, token: Optional[str] = None, github_client: Optional[Github] = None):
    """Cria ou utiliza um cliente do GitHub para acessar o repositório informado.

    - Se github_client for fornecido, ele será usado.
    - Caso contrário, será criado um cliente a partir do token.
    - O token pode ser passado via parâmetro ou lido de os.environ['GITHUB_TOKEN'].
    """
    if github_client is not None:
        return github_client.get_repo(repositorio)

    if token is None:
        token = os.environ.get('GITHUB_TOKEN')

    if not token:
        raise ValueError("Token do GitHub não fornecido. Defina 'GITHUB_TOKEN' no ambiente ou passe via parâmetro 'token'.")

    auth = Token(token)
    g = Github(auth=auth)
    return g.get_repo(repositorio)


MAPEAMENTO_TIPO_EXTENSOES: Dict[str, List[str]] = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}


def _leitura_recursiva_com_debug(repo, extensoes, path: str = "", arquivos_do_repo: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    if arquivos_do_repo is None:
        arquivos_do_repo = {}

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
                    # Propaga o erro para permitir tratamento consistente a montante
                    raise RuntimeError(f"Erro ao decodificar o arquivo '{conteudo.path}': {e}") from e

    return arquivos_do_repo


def main(
    repo: str,
    tipo_de_analise: str,
    github_client: Optional[Github] = None,
    token: Optional[str] = None,
    logger: Optional[Any] = None,
) -> Dict[str, str]:
    """Retorna um dicionário {caminho: conteudo} dos arquivos relevantes para o tipo de análise.

    - Permite injeção de github_client para testes.
    - Lê token do ambiente se não fornecido.
    - Propaga exceções para que o chamador decida o tratamento.
    """
    try:
        repositorio_final = conection(repositorio=repo, token=token, github_client=github_client)
        extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
        arquivos_encontrados = _leitura_recursiva_com_debug(repositorio_final, extensoes=extensoes_alvo)
        return arquivos_encontrados
    except Exception as e:
        if logger:
            try:
                logger.error(f"Falha ao ler repositório '{repo}' para análise '{tipo_de_analise}': {e}")
            except Exception:
                pass
        # Propaga a exceção
        raise
