import os
import logging
from github import Github
from github.Auth import Token

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def conectar_repositorio(repositorio: str):
    """Conecta ao repositório GitHub usando token de acesso.

    Ordem de busca do token:
    1) Variável de ambiente GITHUB_TOKEN
    2) google.colab.userdata['github_token'] (fallback opcional)
    """
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        try:
            from google.colab import userdata  # type: ignore
            token = userdata.get('github_token')
        except Exception:
            token = None

    if not token:
        raise ValueError(
            "Token do GitHub não encontrado. Defina a variável de ambiente GITHUB_TOKEN ou configure via google.colab.userdata['github_token']."
        )

    auth = Token(token)
    g = Github(auth=auth)
    return g.get_repo(repositorio)


MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}


def _deve_incluir_arquivo(path: str, extensoes_alvo):
    """Decide se o arquivo deve ser incluído com base em extensões-alvo."""
    if extensoes_alvo is None:
        # Sem filtro explícito: evitamos alguns binários comuns por extensão.
        extensoes_binarias = (
            ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico",
            ".pdf", ".zip", ".tar", ".gz", ".xz", ".7z",
            ".mp3", ".mp4", ".mov", ".avi", ".ogg",
            ".exe", ".dll", ".so", ".dylib",
        )
        return not path.lower().endswith(extensoes_binarias)
    # Filtro por lista de extensões ou nomes específicos (ex.: Dockerfile)
    return any(path.endswith(ext) or path.split("/")[-1] == ext for ext in extensoes_alvo)


def _listar_caminhos_por_tree(repo, extensoes_alvo, tamanho_max_bytes: int = 200 * 1024):
    """Lista caminhos de arquivos no repo usando a árvore Git recursiva, filtrando por extensão e tamanho."""
    tree = repo.get_git_tree(sha="HEAD", recursive=True)
    caminhos = []
    for entry in tree.tree:
        if entry.type != 'blob':
            continue
        path = entry.path
        if not _deve_incluir_arquivo(path, extensoes_alvo):
            continue
        size = getattr(entry, 'size', None)
        if size is None:
            # Sem tamanho informado, tentamos mesmo assim (algumas APIs podem omitir)
            caminhos.append(path)
            continue
        if size <= tamanho_max_bytes:
            caminhos.append(path)
        else:
            logger.debug("Ignorando arquivo grande %s (%s bytes)", path, size)
    return caminhos


def main(repo, tipo_de_analise: str):
    """Lê arquivos do repositório aplicando estratégia otimizada de listagem e filtragem."""
    repositorio_final = conectar_repositorio(repositorio=repo)

    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())

    arquivos_encontrados = {}
    try:
        caminhos = _listar_caminhos_por_tree(repositorio_final, extensoes_alvo)
        for path in caminhos:
            try:
                conteudo = repositorio_final.get_contents(path)
                codigo = conteudo.decoded_content.decode('utf-8', errors='replace')
                arquivos_encontrados[path] = codigo
            except Exception as e:
                logger.warning("Falha ao ler arquivo '%s': %s", path, e)
    except Exception as e:
        logger.exception("Erro durante a listagem/leitura do repositório '%s'", repo)
        raise

    return arquivos_encontrados
