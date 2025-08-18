import os
from typing import Dict, Optional
from github import Github
from github.Auth import Token

# Suporte opcional ao Google Colab userdata (fallback para variáveis de ambiente)
try:
    from google.colab import userdata as colab_user_data  # type: ignore
except Exception:  # pragma: no cover
    colab_user_data = None  # type: ignore


def _get_secret(nome: str) -> Optional[str]:
    if colab_user_data is not None:
        try:
            val = colab_user_data.get(nome)
            if val:
                return val
        except Exception:
            pass
    return os.getenv(nome)


SKIP_DIRS = {'.git', '.github', 'node_modules', 'dist', 'build', 'venv', '.venv', '__pycache__'}
MAX_FILE_BYTES = int(os.getenv('MAX_GH_FILE_BYTES', '200000'))  # 200KB

MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
    # Padrões de texto para análises gerais
    "design": [
        ".py", ".js", ".ts", ".tsx", ".jsx",
        ".tf", ".tfvars",
        ".json", ".yaml", ".yml",
        ".md", ".markdown",
        ".sh", "Dockerfile"
    ],
    "pentest": [
        ".py", ".js", ".ts", ".tsx", ".jsx",
        ".tf", ".tfvars",
        ".json", ".yaml", ".yml",
        ".md", ".markdown",
        ".sh", "Dockerfile"
    ],
    "seguranca": [
        ".py", ".js", ".ts", ".tsx", ".jsx",
        ".tf", ".tfvars",
        ".json", ".yaml", ".yml",
        ".md", ".markdown",
        ".sh", "Dockerfile"
    ],
}


def _validar_nome_repositorio(repositorio: str) -> None:
    if not isinstance(repositorio, str) or '/' not in repositorio:
        raise ValueError(f"Nome de repositório inválido: '{repositorio}'. Formato esperado: 'owner/repo'.")
    owner, repo = repositorio.split('/', 1)
    if not owner or not repo:
        raise ValueError(f"Nome de repositório inválido: '{repositorio}'. Formato esperado: 'owner/repo'.")


def conectar_github(repositorio: str):
    _validar_nome_repositorio(repositorio)
    token = _get_secret('GITHUB_TOKEN')
    if token:
        auth = Token(token)
        g = Github(auth=auth)
    else:
        print("AVISO: GITHUB_TOKEN não definido. Usando cliente anônimo (limites de rate mais baixos).")
        g = Github()
    return g.get_repo(repositorio)


def _should_read(path: str, name: str, extensoes) -> bool:
    if extensoes is None:
        return True
    # Verifica por extensão e também por nomes exatos (ex.: Dockerfile)
    for ext in extensoes:
        if ext.startswith('.') and path.endswith(ext):
            return True
        if name == ext:
            return True
    return False


def _leitura_recursiva_com_debug(repo, extensoes, path: str = "", arquivos_do_repo: Optional[Dict[str, str]] = None, stats: Optional[Dict[str, int]] = None):
    if arquivos_do_repo is None:
        arquivos_do_repo = {}
    if stats is None:
        stats = {
            'dirs_skipped': 0,
            'files_scanned': 0,
            'files_included': 0,
            'skipped_due_to_size': 0,
            'binary_skipped': 0,
            'decoded_errors': 0,
            'read_errors': 0
        }

    try:
        conteudos = repo.get_contents(path)

        for conteudo in conteudos:
            try:
                if conteudo.type == "dir":
                    dir_name = conteudo.name
                    if dir_name in SKIP_DIRS:
                        stats['dirs_skipped'] += 1
                        continue
                    _leitura_recursiva_com_debug(repo, extensoes, conteudo.path, arquivos_do_repo, stats)
                else:
                    stats['files_scanned'] += 1
                    if not _should_read(conteudo.path, conteudo.name, extensoes):
                        continue

                    # Usa o tamanho reportado pela API sem baixar tudo se for muito grande
                    if getattr(conteudo, 'size', 0) and conteudo.size > MAX_FILE_BYTES:
                        stats['skipped_due_to_size'] += 1
                        continue

                    try:
                        raw = conteudo.decoded_content  # bytes
                    except Exception as de:
                        stats['read_errors'] += 1
                        print(f"DEBUG: ERRO ao obter conteúdo de '{conteudo.path}': {de}")
                        continue

                    if raw is None:
                        continue

                    # Heurística básica para binários
                    if b"\x00" in raw[:8000]:
                        stats['binary_skipped'] += 1
                        continue

                    try:
                        codigo = raw.decode('utf-8', errors='replace')
                    except Exception as e:
                        stats['decoded_errors'] += 1
                        print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")
                        continue

                    arquivos_do_repo[conteudo.path] = codigo
                    stats['files_included'] += 1
            except Exception as inner:
                stats['read_errors'] += 1
                print(f"DEBUG: ERRO processando caminho '{getattr(conteudo, 'path', path)}': {inner}")
    except Exception as e:
        stats['read_errors'] += 1
        print(f"DEBUG: ERRO ao listar conteúdo em '{path}': {e}")

    arquivos_do_repo['__stats__'] = stats
    return arquivos_do_repo


def main(repo: str, tipo_de_analise: str) -> Dict[str, str]:
    repositorio_final = conectar_github(repositorio=repo)
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())

    arquivos_encontrados = _leitura_recursiva_com_debug(
        repositorio_final,
        extensoes=extensoes_alvo,
        path=""
    )

    return arquivos_encontrados
