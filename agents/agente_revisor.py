from typing import Optional, Dict, Any, Protocol

# ===== Abstrações e Estratégias =====

class CodigoSource(Protocol):
    def obter_codigo(self) -> Dict[str, str]:
        ...


class GithubCodigoSource:
    def __init__(self, repositorio: str, tipo_analise: str):
        from tools import github_reader
        self.repositorio = repositorio
        self.tipo_analise = tipo_analise
        self.github_reader = github_reader

    def obter_codigo(self) -> Dict[str, str]:
        print(f'Iniciando a leitura do repositório: {self.repositorio}')
        return self.github_reader.main(repo=self.repositorio, tipo_de_analise=self.tipo_analise)


class CodigoDiretoSource:
    def __init__(self, codigo: str):
        self.codigo = codigo

    def obter_codigo(self) -> Dict[str, str]:
        return self.codigo


class AnaliseExecutor(Protocol):
    def executar(self, tipo_analise: str, codigo: str, analise_extra: str, model_name: str, max_token_out: int) -> Any:
        ...


class OpenAIAnaliseExecutor:
    def __init__(self):
        from tools.revisor_geral import executar_analise_llm
        self.executar_analise_llm = executar_analise_llm

    def executar(self, tipo_analise: str, codigo: str, analise_extra: str, model_name: str, max_token_out: int):
        return self.executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=str(codigo),
            analise_extra=analise_extra,
            model_name=model_name,
            max_token_out=max_token_out
        )


# ===== Validação e Orquestração =====

ANALISES_VALIDAS = ["design", "pentest", "seguranca", "terraform"]
MODELO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000


def validar_parametros(tipo_analise: str, repositorio: Optional[str], codigo: Optional[str]):
    if tipo_analise not in ANALISES_VALIDAS:
        raise ValueError(
            f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {ANALISES_VALIDAS}")
    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")


def criar_codigo_source(tipo_analise: str, repositorio: Optional[str], codigo: Optional[str]) -> CodigoSource:
    if codigo is not None:
        return CodigoDiretoSource(codigo)
    elif repositorio is not None:
        return GithubCodigoSource(repositorio, tipo_analise)
    else:
        raise ValueError("Deve ser fornecido um repositório ou código fonte.")


def executar_analise(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[str] = None,
    instrucoes_extras: str = "",
    model_name: str = MODELO_LLM,
    max_token_out: int = MAX_TOKENS_SAIDA,
    codigo_source: Optional[CodigoSource] = None,
    analise_executor: Optional[AnaliseExecutor] = None
) -> Dict[str, Any]:
    """
    Orquestrador principal desacoplado: valida, obtém código e executa análise via estratégias injetáveis.
    """
    validar_parametros(tipo_analise, repositorio, codigo)

    # Permite injeção de dependências para testabilidade
    if codigo_source is None:
        codigo_source = criar_codigo_source(tipo_analise, repositorio, codigo)
    if analise_executor is None:
        analise_executor = OpenAIAnaliseExecutor()

    codigo_para_analise = codigo_source.obter_codigo()

    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}

    resultado = analise_executor.executar(
        tipo_analise=tipo_analise,
        codigo=codigo_para_analise,
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}
