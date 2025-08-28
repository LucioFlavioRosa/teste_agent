from typing import Optional, Dict, Any, Union
from tools.revisor_geral import executar_analise_llm
from services.validator_service import ValidatorService
from services.error_handler_service import ErrorHandlerService
from services.code_processor_service import CodeProcessorService
from strategies.analysis_strategy_registry import AnalysisStrategyRegistry
import logging

MODELO_PADRAO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

class AgenteRevisor:
    """Agente principal para execução de análises de código seguindo princípios SOLID."""
    
    def __init__(self):
        self.strategy_registry = AnalysisStrategyRegistry()
        self.validator = ValidatorService(self.strategy_registry.get_valid_analysis_types())
        self.code_processor = CodeProcessorService()
        self.error_handler = ErrorHandlerService()
    
    def executar_analise(self,
                        tipo_analise: str,
                        repositorio: Optional[str] = None,
                        codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                        instrucoes_extras: str = "",
                        model_name: str = MODELO_PADRAO_LLM,
                        max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
        """Executa análise de código com arquitetura refatorada seguindo SOLID.
        
        Args:
            tipo_analise: Tipo de análise a ser executada
            repositorio: Nome do repositório (opcional)
            codigo_entrada: Código para análise direta (opcional)
            instrucoes_extras: Instruções adicionais
            model_name: Nome do modelo LLM
            max_token_out: Máximo de tokens na saída
            
        Returns:
            Dict[str, Any]: Resultado da análise
        """
        def _executar_analise_interna():
            # Validação usando serviço dedicado
            self.validator.validar_parametros_entrada(
                tipo_analise=tipo_analise, 
                repositorio_nome=repositorio, 
                codigo_entrada=codigo_entrada
            )
            
            # Preparação do código usando serviço dedicado
            codigo_para_analise = self.code_processor.preparar_codigo_para_analise(
                tipo_analise=tipo_analise, 
                repositorio_nome=repositorio, 
                codigo_entrada=codigo_entrada
            )
            
            if not codigo_para_analise:
                logging.warning('Não foi fornecido nenhum código para análise.')
                return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
            
            # Formatação do código para LLM
            codigo_final = self.code_processor.montar_codigo_para_llm(codigo_para_analise)
            
            # Execução da análise LLM
            resultado = executar_analise_llm(
                tipo_analise=tipo_analise,
                codigo=codigo_final,
                analise_extra=instrucoes_extras,
                model_name=model_name,
                max_token_out=max_token_out
            )
            
            return {"tipo_analise": tipo_analise, "resultado": resultado}
        
        # Execução com tratamento centralizado de erros
        return self.error_handler.executar_com_tratamento(_executar_analise_interna)

# Instância global para manter compatibilidade com API existente
_agente_revisor_instance = AgenteRevisor()

# Funções de compatibilidade para manter API existente
def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_PADRAO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    """Função de compatibilidade para manter API existente."""
    return _agente_revisor_instance.executar_analise(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo_entrada=codigo_entrada,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
