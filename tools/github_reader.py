import re
from github import Github
from github.Auth import Token
import os


def conection(repositorio: str, github_token: str):
    auth = Token(github_token)
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


def main(repo, tipo_de_analise: str, github_token: str):

    repositorio_final = conection(repositorio=repo, github_token=github_token)

    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())

    arquivos_encontrados = _leitura_recursiva_com_debug(repositorio_final,
                                                        extensoes=extensoes_alvo)

    return arquivos_encontrados
