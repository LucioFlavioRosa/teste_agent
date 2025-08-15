import os
from typing import Optional, Dict, Any, List
from tools.github_reader import GithubRepositoryReader, FileFilterByExtensions
from tools.revisor_geral import executar_analise_llm, PromptRepositoryFS, OpenAIClient
from core.ports import ICodeRepositoryReader, ILLMClient, PromptRepository


modelo_llm = 'gpt-4.1'
max_tokens_saida = 3000

# Configuração de filtragem por tipo de análise (pode ser estendida sem alterar o crawler)
ANALISE_EXTENSIONS = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}


def get_valid_analysis_types(prompt_repo: PromptRepository) -> List[str]:
    return prompt_repo.list_types()


def get_file_filter(tipo_analise: str) -> FileFilterByExtensions:
    exts = ANALISE_EXTENSIONS.get((tipo_analise or '').lower())
    return FileFilterByExtensions(exts)


def validate_inputs(tipo_analise: str,
                    tipos_validos: List[str],
                    repositorio: Optional[str] = None,
                    codigo: Optional[str] = None) -> None:
    if tipo_analise not in tipos_validos:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {tipos_validos}")
    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")


def resolve_code_source(reader: ICodeRepositoryReader,
                        tipo_analise: str,
                        repositorio: Optional[str] = None,
                        codigo: Optional[str] = None):
    if codigo is not None:
        return codigo
    if not repositorio:
        return None
    filtro = get_file_filter(tipo_analise)
    return reader.read_repo(repositorio, filtro)


def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo: Optional[str] = None,
                     instrucoes_extras: str = "",
                     model_name: str = modelo_llm,
                     max_token_out: int = max_tokens_saida,
                     repo_reader: Optional[ICodeRepositoryReader] = None,
                     prompt_repo: Optional[PromptRepository] = None,
                     llm_client: Optional[ILLMClient] = None) -> Dict[str, Any]:

    # Fábricas padrão (quando não injetado explicitamente)
    if prompt_repo is None:
        prompt_repo = PromptRepositoryFS()
    if repo_reader is None:
        token = os.environ.get('GITHUB_TOKEN')
        repo_reader = GithubRepositoryReader(token=token)
    if llm_client is None:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrado no ambiente e nenhum ILLMClient foi fornecido.")
        llm_client = OpenAIClient(api_key=api_key)

    tipos_validos = get_valid_analysis_types(prompt_repo)
    validate_inputs(tipo_analise=tipo_analise,
                    tipos_validos=tipos_validos,
                    repositorio=repositorio,
                    codigo=codigo)

    codigo_para_analise = resolve_code_source(reader=repo_reader,
                                              tipo_analise=tipo_analise,
                                              repositorio=repositorio,
                                              codigo=codigo)

    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}

    resultado = executar_analise_llm(
        tipo_analise=tipo_analise,
        codigo=str(codigo_para_analise),
        analise_extra=instrucoes_extras,
        client=llm_client,
        prompt_repo=prompt_repo,
        model_name=model_name,
        max_token_out=max_token_out,
    )

    return {"tipo_analise": tipo_analise, "resultado": resultado}


# Alias para compatibilidade retrocompatível
main = executar_analise
