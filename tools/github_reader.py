import os
import logging
from github import Github


def conection(repositorio: str, token: str | None = None, gh: Github | None = None):
    """Cria conexão com o repositório, permitindo DI do cliente e leitura de token via env.

    - token: opcional; quando não informado, usa a variável de ambiente GITHUB_TOKEN.
    - gh: instancia de Github já construída (para testes/mocks). Quando fornecida, tem precedência.
    """
    ghc = gh or Github(auth=(token or os.getenv('GITHUB_TOKEN')))
    return ghc.get_repo(repositorio)


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
                        logging.debug("Erro na decodificação de '%s': %s", conteudo.path, e)

    except Exception as e:
        logging.error("Erro ao ler caminho '%s': %s", path, e)

    return arquivos_do_repo


def main(repo, tipo_de_analise: str):

    repositorio_final = conection(repositorio=repo)

    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())

    arquivos_encontrados = _leitura_recursiva_com_debug(repositorio_final, extensoes=extensoes_alvo)

    return arquivos_encontrados
