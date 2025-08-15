import os
from github import Github
from github.Auth import Token


def conection(repositorio: str):
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        auth = Token(token)
        g = Github(auth=auth)
    else:
        # Conexão anônima (rate limited). Opcionalmente, informe GITHUB_TOKEN para aumentar limites.
        g = Github()
    return g.get_repo(repositorio)


MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
    # Mapeamentos adicionados para evitar varredura irrestrita
    "design": [".py", ".md", ".txt", ".yaml", ".yml", ".tf", "Dockerfile"],
    "pentest": [".py", ".sh", ".md", "Dockerfile"],
    "seguranca": [".py", ".tf", ".yaml", ".yml", ".md", "Dockerfile"],
}


def _leitura_recursiva_com_debug(repo, extensoes, path="", arquivos_do_repo=None, max_arquivos=200, max_tamanho=256 * 1024):

    if arquivos_do_repo is None:
        arquivos_do_repo = {}

    # Encerrar cedo se já atingiu o limite
    if len(arquivos_do_repo) >= max_arquivos:
        return arquivos_do_repo

    try:
        conteudos = repo.get_contents(path)

        for conteudo in conteudos:
            if len(arquivos_do_repo) >= max_arquivos:
                break

            if conteudo.type == "dir":
                _leitura_recursiva_com_debug(repo, extensoes, conteudo.path, arquivos_do_repo, max_arquivos, max_tamanho)
            else:
                ler_o_arquivo = False
                if extensoes:
                    if any(conteudo.path.endswith(ext) for ext in extensoes) or conteudo.name in extensoes:
                        ler_o_arquivo = True

                if ler_o_arquivo:
                    try:
                        # Limite de tamanho
                        tamanho = getattr(conteudo, 'size', None)
                        if tamanho is not None and tamanho > max_tamanho:
                            continue

                        # Leitura segura e detecção de binários
                        bruto = conteudo.decoded_content
                        if bruto is None:
                            continue
                        if b"\x00" in bruto:
                            # Indício de arquivo binário
                            continue
                        try:
                            codigo = bruto.decode('utf-8')
                        except Exception:
                            # Não UTF-8, ignorar
                            continue

                        arquivos_do_repo[conteudo.path] = codigo
                    except Exception:
                        # Ignora erros por arquivo individual
                        continue

    except Exception:
        # Silencia erros de leitura de diretórios não acessíveis
        pass
        
    return arquivos_do_repo


def main(repo, tipo_de_analise: str):

    repositorio_final = conection(repositorio=repo)

    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
    if not extensoes_alvo:
        raise ValueError(f"Tipo de análise '{tipo_de_analise}' não mapeado para extensões suportadas.")

    arquivos_encontrados = _leitura_recursiva_com_debug(
        repositorio_final,
        extensoes=extensoes_alvo
    )
  
    return arquivos_encontrados
