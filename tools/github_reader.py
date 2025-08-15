import base64
from typing import Dict, Optional, List, Tuple
from github import Github
from github.Auth import Token
from google.colab import userdata

# ============================
# Configurações e Constantes
# ============================

# Diretórios a serem ignorados durante a varredura
EXCLUDED_DIRS = {
    '.git', 'node_modules', 'dist', 'build', 'vendor', '.venv', '.cache',
    '__pycache__', '.idea', '.vscode', 'target', 'bin', 'obj', '.mypy_cache',
}

# Limites padrão
DEFAULT_MAX_FILES = 200
DEFAULT_MAX_BYTES_TOTAL = 4 * 1024 * 1024  # 4 MiB
DEFAULT_MAX_FILE_SIZE = 200 * 1024         # 200 KiB

# Mapeamento de extensões/nomes por tipo de análise
# Observação: valores podem ser extensões (e.g., .py) ou nomes exatos (e.g., Dockerfile)
MAPEAMENTO_TIPO_EXTENSOES = {
    'terraform': ['.tf', '.tfvars'],
    'python': ['.py'],
    'cloudformation': ['.json', '.yaml', '.yml'],
    'ansible': ['.yml', '.yaml'],
    'docker': ['Dockerfile'],
    # Coberturas amplas para análises "design", "pentest", "seguranca"
    'design': [
        '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.rb', '.go', '.rs', '.cs', '.cpp', '.c', '.h', '.hpp',
        '.php', '.sh', '.bash', '.ps1', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
        '.tf', '.tfvars', '.md', '.txt', '.env', '.properties', '.gradle', '.kts',
        'Dockerfile', 'Makefile'
    ],
    'pentest': [
        '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.rb', '.go', '.rs', '.cs', '.cpp', '.c', '.h', '.hpp',
        '.php', '.sh', '.bash', '.ps1', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
        '.tf', '.tfvars', '.md', '.txt', '.env', '.properties',
        'Dockerfile', 'Makefile'
    ],
    'seguranca': [
        '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.rb', '.go', '.rs', '.cs', '.cpp', '.c', '.h', '.hpp',
        '.php', '.sh', '.bash', '.ps1', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
        '.tf', '.tfvars', '.md', '.txt', '.env', '.properties',
        'Dockerfile', 'Makefile'
    ],
}

# Cache simples em memória por SHA de referência
# Chave: (repo_full_name, ref_sha, tipo_analise, max_files, max_bytes_total, max_file_size)
# Valor: dict[path] = conteudo (com chave especial '__meta__')
_CACHE: Dict[Tuple[str, str, str, int, int, int], Dict[str, str]] = {}


def conection(repositorio: str):
    """Abre conexão autenticada com o repositório."""
    GITHUB_TOKEN = userdata.get('github_token')
    auth = Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    return g.get_repo(repositorio)


def _is_excluded(path: str) -> bool:
    parts = path.split('/')
    return any(p in EXCLUDED_DIRS for p in parts)


def _resolve_ref_sha(repo, ref: Optional[str]) -> str:
    """Resolve um branch/tag/sha em um SHA de commit."""
    if ref and len(ref) == 40 and all(c in '0123456789abcdef' for c in ref.lower()):
        return ref
    if ref:
        # Branch ou tag
        try:
            return repo.get_branch(ref).commit.sha
        except Exception:
            try:
                return repo.get_git_ref(f'heads/{ref}').object.sha
            except Exception:
                pass
    # Padrão: branch default
    return repo.get_branch(repo.default_branch).commit.sha


def _is_text_bytes(b: bytes) -> bool:
    """Heurística simples para detectar binários."""
    if b"\x00" in b:
        return False
    # Considera texto se a maioria é imprimível/whitespace
    try:
        s = b.decode('utf-8')
        return True
    except Exception:
        return False


def _match_ext_or_name(path: str, nome: str, extensoes_ou_nomes: List[str]) -> bool:
    if not extensoes_ou_nomes:
        return False
    for x in extensoes_ou_nomes:
        if x.startswith('.') and path.endswith(x):
            return True
        if nome == x:
            return True
    return False


def main(
    repo: str,
    tipo_de_analise: str,
    ref: Optional[str] = None,
    max_files: int = DEFAULT_MAX_FILES,
    max_bytes_total: int = DEFAULT_MAX_BYTES_TOTAL,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE,
) -> Dict[str, str]:
    """
    Lê arquivos alvo de um repositório via Git Tree recursivo, com filtros de
    diretórios, extensões, limites de tamanho/quantidade e detecção de binários.

    Retorna um dicionário { caminho: conteudo }, com uma chave especial '__meta__'
    contendo metadados como ref_sha e limites utilizados.
    """
    repositorio = conection(repositorio=repo)

    tipo = (tipo_de_analise or '').lower()
    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo)
    if extensoes_alvo is None:
        # Se tipo não mapeado, use um conjunto amplo por segurança (não ler repositório inteiro)
        extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES['design']

    ref_sha = _resolve_ref_sha(repositorio, ref)

    cache_key = (
        repositorio.full_name,
        ref_sha,
        tipo,
        int(max_files),
        int(max_bytes_total),
        int(max_file_size),
    )
    if cache_key in _CACHE:
        return _CACHE[cache_key]

    # Obtem a árvore completa (uma chamada recursiva)
    tree = repositorio.get_git_tree(ref_sha, recursive=True)

    resultado: Dict[str, str] = {}
    total_bytes = 0
    count_files = 0

    for item in tree.tree:
        if item.type != 'blob':
            continue
        path = item.path
        if _is_excluded(path):
            continue
        name = path.split('/')[-1]
        if not _match_ext_or_name(path, name, extensoes_alvo):
            continue
        # Filtra por tamanho
        size = getattr(item, 'size', None)
        if size is not None and size > max_file_size:
            continue
        if count_files >= max_files:
            break
        if total_bytes >= max_bytes_total:
            break

        try:
            # Buscar blob diretamente para evitar chamada por arquivo via get_contents
            blob = repositorio.get_git_blob(item.sha)
            raw = base64.b64decode(blob.content)
            if not _is_text_bytes(raw):
                continue
            # Limita por tamanho do arquivo após decodificação
            if len(raw) > max_file_size:
                continue
            # Atualiza limites totais
            if total_bytes + len(raw) > max_bytes_total:
                continue
            conteudo = raw.decode('utf-8', errors='replace')
            resultado[path] = conteudo
            total_bytes += len(raw)
            count_files += 1
        except Exception as e:
            print(f"DEBUG: Falha ao ler blob '{path}': {e}")
            continue

    # Metadados úteis (não devem ser enviados diretamente ao LLM)
    resultado['__meta__'] = {
        'repo': repositorio.full_name,
        'ref_sha': ref_sha,
        'limits': {
            'max_files': max_files,
            'max_bytes_total': max_bytes_total,
            'max_file_size': max_file_size,
            'selected_files': count_files,
            'selected_bytes': total_bytes,
        },
        'tipo_de_analise': tipo,
        'extensoes_alvo': extensoes_alvo,
    }

    _CACHE[cache_key] = resultado
    return resultado
