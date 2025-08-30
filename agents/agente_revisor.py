from typing import Optional, Dict, Any, Union
from tools import github_reader
from tools.revisor_geral import executar_analise_llm
from core.validators import ParameterValidator
from core.error_handlers import ErrorHandler
from core.code_processor import CodeProcessor
import logging

MODELO_PADRAO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

class AgentRevisor:
    """Agente responsável pela execução de análises de código."""
    
    def __init__(self):
        self.validator = ParameterValidator()
        self.error_handler = ErrorHandler()
        self.code_processor = CodeProcessor()
    
    def executar_analise(self, 
                        tipo_analise: str,
                        repositorio: Optional[str] = None,
                        codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                        instrucoes_extras: str = "",
                        model_name: str = MODELO_PADRAO_LLM,
                        max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
        """Executa análise de código com base nos parâmetros fornecidos."""
        try:
            # Validação de parâmetros
            self.validator.validar_parametros_entrada(
                tipo_analise=tipo_analise, 
                repositorio_nome=repositorio, 
                codigo_entrada=codigo_entrada
            )
            
            # Preparação do código
            codigo_para_analise = self.code_processor.preparar_codigo_para_analise(
                tipo_analise=tipo_analise, 
                repositorio_nome=repositorio, 
                codigo_entrada=codigo_entrada
            )
            
            if not codigo_para_analise:
                logging.warning('Não foi fornecido nenhum código para análise.')
                return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
            
            # Montagem do código final
            codigo_final = self.code_processor.montar_codigo_para_llm(codigo_para_analise)
            
            # Execução da análise
            resultado = executar_analise_llm(
                tipo_analise=tipo_analise,
                codigo=codigo_final,
                analise_extra=instrucoes_extras,
                model_name=model_name,
                max_token_out=max_token_out
            )
            
            return {"tipo_analise": tipo_analise, "resultado": resultado}
            
        except Exception as e:
            return self.error_handler.handle_error(e)

# Instância global para compatibilidade com código existente
_agente_revisor = AgentRevisor()

# Funções de compatibilidade
def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_PADRAO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    """Função de compatibilidade para manter a API existente."""
    return _agente_revisor.executar_analise(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo_entrada=codigo_entrada,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )