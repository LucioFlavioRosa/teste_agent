from typing import Optional, Dict, Any
from agents.interfaces import ICodeReader, IAnalysisExecutor
from agents.services import GitHubCodeReader, LLMAnalysisExecutor
from agents.validators import AnalysisValidator
from agents.registry import analysis_registry


class AgenteRevisor:
    """Orquestrador principal para execução de análises de código."""
    
    def __init__(
        self,
        code_reader: ICodeReader = None,
        analysis_executor: IAnalysisExecutor = None,
        modelo_llm: str = 'gpt-4.1',
        max_tokens_saida: int = 3000
    ):
        """Inicializa o agente revisor com dependências injetadas.
        
        Args:
            code_reader: Implementação para leitura de código
            analysis_executor: Implementação para execução de análises
            modelo_llm: Modelo LLM padrão
            max_tokens_saida: Máximo de tokens de saída padrão
        """
        self._code_reader = code_reader or GitHubCodeReader()
        self._analysis_executor = analysis_executor or LLMAnalysisExecutor()
        self._validator = AnalysisValidator(analysis_registry.get_registered_types())
        self._modelo_llm = modelo_llm
        self._max_tokens_saida = max_tokens_saida
    
    def executar_analise(
        self,
        tipo_analise: str,
        repositorio: Optional[str] = None,
        codigo: Optional[str] = None,
        instrucoes_extras: str = "",
        model_name: str = None,
        max_token_out: int = None
    ) -> Dict[str, Any]:
        """Executa análise de código com base nos parâmetros fornecidos.
        
        Args:
            tipo_analise: Tipo de análise a executar
            repositorio: Nome do repositório (opcional)
            codigo: Código direto para análise (opcional)
            instrucoes_extras: Instruções extras para análise
            model_name: Nome do modelo LLM (usa padrão se None)
            max_token_out: Máximo de tokens de saída (usa padrão se None)
            
        Returns:
            Dicionário com tipo de análise e resultado
            
        Raises:
            ValueError: Se parâmetros inválidos forem fornecidos
            RuntimeError: Se falhar ao executar a análise
        """
        # Usa valores padrão se não fornecidos
        model_name = model_name or self._modelo_llm
        max_token_out = max_token_out or self._max_tokens_saida
        
        # Validações
        self._validator.validate_analysis_type(tipo_analise)
        self._validator.validate_input_sources(repositorio, codigo)
        
        # Obtenção do código
        codigo_para_analise = self._get_code_for_analysis(
            tipo_analise, repositorio, codigo
        )
        
        if not codigo_para_analise:
            return {
                "tipo_analise": tipo_analise,
                "resultado": 'Não foi fornecido nenhum código para análise'
            }
        
        # Execução da análise
        try:
            resultado = self._analysis_executor.execute_analysis(
                tipo_analise=tipo_analise,
                codigo=str(codigo_para_analise),
                analise_extra=instrucoes_extras,
                model_name=model_name,
                max_token_out=max_token_out
            )
            
            return {"tipo_analise": tipo_analise, "resultado": resultado}
            
        except Exception as e:
            raise RuntimeError(
                f"Falha ao executar análise '{tipo_analise}': {e}"
            ) from e
    
    def _get_code_for_analysis(
        self,
        tipo_analise: str,
        repositorio: Optional[str],
        codigo: Optional[str]
    ) -> str:
        """Obtém o código para análise da fonte apropriada.
        
        Args:
            tipo_analise: Tipo de análise
            repositorio: Nome do repositório (opcional)
            codigo: Código direto (opcional)
            
        Returns:
            Código para análise
        """
        if codigo is not None:
            return codigo
        
        if repositorio is not None:
            return self._code_reader.read_code(repositorio, tipo_analise)
        
        return ""


# Instância global para compatibilidade com código existente
_agente_revisor_instance = AgenteRevisor()


# Funções de compatibilidade para manter API existente
def executar_analise(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[str] = None,
    instrucoes_extras: str = "",
    model_name: str = 'gpt-4.1',
    max_token_out: int = 3000
) -> Dict[str, Any]:
    """Função de compatibilidade para executar análise.
    
    Args:
        tipo_analise: Tipo de análise a executar
        repositorio: Nome do repositório (opcional)
        codigo: Código direto para análise (opcional)
        instrucoes_extras: Instruções extras para análise
        model_name: Nome do modelo LLM
        max_token_out: Máximo de tokens de saída
        
    Returns:
        Dicionário com tipo de análise e resultado
    """
    return _agente_revisor_instance.executar_analise(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo=codigo,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )


def main(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[str] = None,
    instrucoes_extras: str = "",
    model_name: str = 'gpt-4.1',
    max_token_out: int = 3000
) -> Dict[str, Any]:
    """Função de compatibilidade main para manter API existente.
    
    Args:
        tipo_analise: Tipo de análise a executar
        repositorio: Nome do repositório (opcional)
        codigo: Código direto para análise (opcional)
        instrucoes_extras: Instruções extras para análise
        model_name: Nome do modelo LLM
        max_token_out: Máximo de tokens de saída
        
    Returns:
        Dicionário com tipo de análise e resultado
    """
    return executar_analise(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo=codigo,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
