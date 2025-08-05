from typing import Optional, Dict, Any
from tools.github_reader import GithubRepositoryReader
from tools.revisor_geral import LLMAnalyzer


class AnalysisStrategy:
    """
    Interface para estratégias de análise. Permite extensão fácil para novos tipos.
    """
    def analyze(self, codigo_para_analise: str, instrucoes_extras: str, llm_analyzer: LLMAnalyzer, model_name: str, max_token_out: int) -> Dict[str, Any]:
        raise NotImplementedError


class DesignAnalysisStrategy(AnalysisStrategy):
    def analyze(self, codigo_para_analise: str, instrucoes_extras: str, llm_analyzer: LLMAnalyzer, model_name: str, max_token_out: int) -> Dict[str, Any]:
        resultado = llm_analyzer.executar_analise_llm(
            tipo_analise='design',
            codigo=str(codigo_para_analise),
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        return {"tipo_analise": "design", "resultado": resultado}


class PentestAnalysisStrategy(AnalysisStrategy):
    def analyze(self, codigo_para_analise: str, instrucoes_extras: str, llm_analyzer: LLMAnalyzer, model_name: str, max_token_out: int) -> Dict[str, Any]:
        resultado = llm_analyzer.executar_analise_llm(
            tipo_analise='pentest',
            codigo=str(codigo_para_analise),
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        return {"tipo_analise": "pentest", "resultado": resultado}


class SegurancaAnalysisStrategy(AnalysisStrategy):
    def analyze(self, codigo_para_analise: str, instrucoes_extras: str, llm_analyzer: LLMAnalyzer, model_name: str, max_token_out: int) -> Dict[str, Any]:
        resultado = llm_analyzer.executar_analise_llm(
            tipo_analise='seguranca',
            codigo=str(codigo_para_analise),
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        return {"tipo_analise": "seguranca", "resultado": resultado}


class TerraformAnalysisStrategy(AnalysisStrategy):
    def analyze(self, codigo_para_analise: str, instrucoes_extras: str, llm_analyzer: LLMAnalyzer, model_name: str, max_token_out: int) -> Dict[str, Any]:
        resultado = llm_analyzer.executar_analise_llm(
            tipo_analise='terraform',
            codigo=str(codigo_para_analise),
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        return {"tipo_analise": "terraform", "resultado": resultado}


ANALYSIS_STRATEGY_MAP = {
    'design': DesignAnalysisStrategy(),
    'pentest': PentestAnalysisStrategy(),
    'seguranca': SegurancaAnalysisStrategy(),
    'terraform': TerraformAnalysisStrategy(),
}


class AgentOrchestrator:
    """
    Orquestrador principal para análise. Desacopla validação, leitura e execução de análise.
    """
    def __init__(self, github_reader=None, llm_analyzer=None):
        self.github_reader = github_reader or GithubRepositoryReader()
        self.llm_analyzer = llm_analyzer or LLMAnalyzer()

    def validar_tipo_analise(self, tipo_analise: str):
        if tipo_analise not in ANALYSIS_STRATEGY_MAP:
            raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {list(ANALYSIS_STRATEGY_MAP.keys())}")

    def obter_codigo_para_analise(self, tipo_analise: str, repositorio: Optional[str], codigo: Optional[str]) -> str:
        if repositorio is None and codigo is None:
            raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")
        if codigo is None:
            print(f'Iniciando a leitura do repositório: {repositorio}')
            return self.github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo

    def executar_analise(self, tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None, instrucoes_extras: str = "", model_name: str = 'gpt-4.1', max_token_out: int = 3000) -> Dict[str, Any]:
        self.validar_tipo_analise(tipo_analise)
        codigo_para_analise = self.obter_codigo_para_analise(tipo_analise, repositorio, codigo)
        if not codigo_para_analise:
            return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
        strategy = ANALYSIS_STRATEGY_MAP[tipo_analise]
        return strategy.analyze(
            codigo_para_analise,
            instrucoes_extras,
            self.llm_analyzer,
            model_name,
            max_token_out
        )

# Instância padrão do orquestrador para uso externo
agent_orchestrator = AgentOrchestrator()

# API legada para compatibilidade
executar_analise = agent_orchestrator.executar_analise
