import re
from github import Github
from github.Auth import Token
from google.colab import userdata
from typing import Dict, Optional


def conection(repositorio: str):
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


def _leitura_recursiva_com_debug(repo, extensoes, path: str = "", arquivos_do_repo: Optional[Dict[str, str]] = None, profundidade: int = 0, max_profundidade: int = 10):
    if arquivos_do_repo is None:
        arquivos_do_repo = {}
    if profundidade > max_profundidade:
        print(f"DEBUG: Profundidade máxima ({max_profundidade}) atingida em '{path}'")
        return arquivos_do_repo
    try:
        conteudos = repo.get_contents(path)
        for conteudo in conteudos:
            if conteudo.type == "dir":
                _leitura_recursiva_com_debug(repo, extensoes, conteudo.path, arquivos_do_repo, profundidade + 1, max_profundidade)
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
        print(f"DEBUG: Falha ao ler '{path}': {e}")
    return arquivos_do_repo


def main(repo, tipo_de_analise: str, max_profundidade: int = 10):
    repositorio_final = conection(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    arquivos_encontrados = _leitura_recursiva_com_debug(repositorio_final,
                                                        extensoes=extensoes_alvo,
                                                        max_profundidade=max_profundidade)
    return arquivos_encontrados
