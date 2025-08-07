from typing import Optional, Dict, Any
from tools.github_reader import GitHubRepositoryReader
from tools.revisor_geral import LLMAnalyzer


class AnalysisStrategy:
    """
    Strategy base para diferentes tipos de análise.
    """
    def analyze(self, codigo: str, instrucoes_extras: str, model_name: str, max_token_out: int) -> Any:
        raise NotImplementedError


class DesignAnalysisStrategy(AnalysisStrategy):
    def __init__(self, analyzer: LLMAnalyzer):
        self.analyzer = analyzer

    def analyze(self, codigo: str, instrucoes_extras: str, model_name: str, max_token_out: int) -> Any:
        return self.analyzer.executar_analise_llm(
            tipo_analise="design",
            codigo=codigo,
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )


class PentestAnalysisStrategy(AnalysisStrategy):
    def __init__(self, analyzer: LLMAnalyzer):
        self.analyzer = analyzer

    def analyze(self, codigo: str, instrucoes_extras: str, model_name: str, max_token_out: int) -> Any:
        return self.analyzer.executar_analise_llm(
            tipo_analise="pentest",
            codigo=codigo,
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )


class SecurityAnalysisStrategy(AnalysisStrategy):
    def __init__(self, analyzer: LLMAnalyzer):
        self.analyzer = analyzer

    def analyze(self, codigo: str, instrucoes_extras: str, model_name: str, max_token_out: int) -> Any:
        return self.analyzer.executar_analise_llm(
            tipo_analise="seguranca",
            codigo=codigo,
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )


class TerraformAnalysisStrategy(AnalysisStrategy):
    def __init__(self, analyzer: LLMAnalyzer):
        self.analyzer = analyzer

    def analyze(self, codigo: str, instrucoes_extras: str, model_name: str, max_token_out: int) -> Any:
        return self.analyzer.executar_analise_llm(
            tipo_analise="terraform",
            codigo=codigo,
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )


class AnalysisService:
    """
    Classe de orquestração para análise, separando responsabilidades.
    """
    ANALYSIS_STRATEGY_MAP = {
        "design": DesignAnalysisStrategy,
        "pentest": PentestAnalysisStrategy,
        "seguranca": SecurityAnalysisStrategy,
        "terraform": TerraformAnalysisStrategy,
    }

    def __init__(self, repo_reader=None, analyzer=None):
        self.repo_reader = repo_reader or GitHubRepositoryReader()
        self.analyzer = analyzer or LLMAnalyzer()

    def get_strategy(self, tipo_analise: str) -> AnalysisStrategy:
        strategy_cls = self.ANALYSIS_STRATEGY_MAP.get(tipo_analise)
        if not strategy_cls:
            raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {list(self.ANALYSIS_STRATEGY_MAP.keys())}")
        return strategy_cls(self.analyzer)

    def get_code(self, repositorio: Optional[str], tipo_analise: str, codigo: Optional[str]) -> Any:
        if repositorio:
            return self.repo_reader.read_repository(repo=repositorio, tipo_de_analise=tipo_analise)
        elif codigo:
            return codigo
        else:
            raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")

    def executar_analise(self,
                         tipo_analise: str,
                         repositorio: Optional[str] = None,
                         codigo: Optional[str] = None,
                         instrucoes_extras: str = "",
                         model_name: str = "gpt-4.1",
                         max_token_out: int = 3000) -> Dict[str, Any]:
        strategy = self.get_strategy(tipo_analise)
        codigo_para_analise = self.get_code(repositorio, tipo_analise, codigo)
        if not codigo_para_analise:
            return {"tipo_analise": tipo_analise, "resultado": "Não foi fornecido nenhum código para análise"}
        resultado = strategy.analyze(
            codigo=str(codigo_para_analise),
            instrucoes_extras=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        return {"tipo_analise": tipo_analise, "resultado": resultado}


# Instância padrão do serviço para integração backward compatible
analysis_service = AnalysisService()


def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo: Optional[str] = None,
                     instrucoes_extras: str = "",
                     model_name: str = "gpt-4.1",
                     max_token_out: int = 3000) -> Dict[str, Any]:
    """
    Função de entrada para manter compatibilidade. Encaminha para o serviço desacoplado.
    """
    return analysis_service.executar_analise(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo=codigo,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
