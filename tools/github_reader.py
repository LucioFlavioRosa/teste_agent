from typing import Dict, Optional, List
from github import Github
from github.Auth import Token
from core.ports import IFileFilter, ICodeRepositoryReader


# Mapeamento mantido para conveniência; pode ser configurado externamente
MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}


class FileFilterByExtensions(IFileFilter):
    """Estratégia de filtragem por extensões e/ou nomes de arquivos."""

    def __init__(self, extensoes: Optional[List[str]] = None) -> None:
        self._extensoes = extensoes

    def should_read(self, path: str, name: str) -> bool:
        if self._extensoes is None:
            return True
        # Lê por nome exato ou por extensão
        for ext in self._extensoes:
            if name == ext:
                return True
            if ext.startswith('.') and path.endswith(ext):
                return True
        return False


class GithubRepositoryReader(ICodeRepositoryReader):
    """Leitor de repositórios GitHub desacoplado de segredos e configuração externa."""

    def __init__(self, token: Optional[str] = None, github_client: Optional[Github] = None) -> None:
        if github_client is not None:
            self._client = github_client
        else:
            if token:
                self._client = Github(auth=Token(token))
            else:
                # Cliente sem autenticação (rate-limitado)
                self._client = Github()

    def read_repo(self, repositorio: str, file_filter: IFileFilter) -> Dict[str, str]:
        repo = self._client.get_repo(repositorio)
        arquivos: Dict[str, str] = {}
        self._read_recursive(repo, '', file_filter, arquivos)
        return arquivos

    def _read_recursive(self, repo, path: str, file_filter: IFileFilter, out: Dict[str, str]) -> None:
        try:
            conteudos = repo.get_contents(path)
        except Exception as e:
            print(f"DEBUG: Falha ao listar path '{path}': {e}")
            return

        for conteudo in conteudos:
            try:
                if conteudo.type == 'dir':
                    self._read_recursive(repo, conteudo.path, file_filter, out)
                else:
                    if file_filter.should_read(conteudo.path, conteudo.name):
                        try:
                            codigo = conteudo.decoded_content.decode('utf-8')
                            out[conteudo.path] = codigo
                        except Exception as e:
                            print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")
            except Exception as e:
                print(f"DEBUG: Erro ao processar '{getattr(conteudo, 'path', '?')}': {e}")
