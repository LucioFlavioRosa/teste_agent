from typing import Optional, Dict, Any
from tools import github_reader
from tools.revisor_geral import AnaliseExecutor


class AnaliseValidator:
    """
    Responsável por validar parâmetros para análise.
    """
    def __init__(self, analises_validas=None):
        if analises_validas is None:
            analises_validas = ["design", "pentest", "seguranca", "terraform"]
        self.analises_validas = analises_validas

    def validar_tipo_analise(self, tipo_analise: str):
        if tipo_analise not in self.analises_validas:
            raise ValueError(
                f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {self.analises_validas}")

    def validar_entrada(self, repositorio: Optional[str], codigo: Optional[str]):
        if repositorio is None and codigo is None:
            raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")


class CodigoProvider:
    """
    Responsável por obter o código a ser analisado, seja de um repositório ou diretamente.
    """
    def __init__(self, repositorio_leitor=None):
        self.repositorio_leitor = repositorio_leitor or github_reader

    def obter_codigo(self, repositorio: Optional[str], tipo_analise: str, codigo: Optional[str]) -> str:
        if codigo is not None:
            return codigo
        if repositorio is not None:
            print(f'Iniciando a leitura do repositório: {repositorio}')
            return self.repositorio_leitor.main(repo=repositorio, tipo_de_analise=tipo_analise)
        return ""


class AnaliseOrquestrador:
    """
    Orquestra o fluxo de validação, obtenção de código e execução da análise.
    """
    def __init__(self, validator=None, codigo_provider=None, executor=None):
        self.validator = validator or AnaliseValidator()
        self.codigo_provider = codigo_provider or CodigoProvider()
        self.executor = executor or AnaliseExecutor()

    def executar_analise(self,
                        tipo_analise: str,
                        repositorio: Optional[str] = None,
                        codigo: Optional[str] = None,
                        instrucoes_extras: str = "",
                        model_name: str = 'gpt-4.1',
                        max_token_out: int = 3000) -> Dict[str, Any]:
        self.validator.validar_tipo_analise(tipo_analise)
        self.validator.validar_entrada(repositorio, codigo)
        codigo_para_analise = self.codigo_provider.obter_codigo(
            repositorio=repositorio,
            tipo_analise=tipo_analise,
            codigo=codigo
        )
        if not codigo_para_analise:
            return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
        resultado = self.executor.executar(
            tipo_analise=tipo_analise,
            codigo=str(codigo_para_analise),
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        return {"tipo_analise": tipo_analise, "resultado": resultado}

# API de alto nível para uso externo
analise_orquestrador = AnaliseOrquestrador()

def executar_analise(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[str] = None,
    instrucoes_extras: str = "",
    model_name: str = 'gpt-4.1',
    max_token_out: int = 3000
) -> Dict[str, Any]:
    """
    Função de fachada para executar uma análise de código desacoplada.
    """
    return analise_orquestrador.executar_analise(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo=codigo,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
