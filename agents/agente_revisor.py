from typing import Optional, Dict, Any, Union
from tools import github_reader
from tools.revisor_geral import executar_analise_llm
from core.validators import ParameterValidator
from core.code_processor import CodeProcessor
from core.analysis_registry import AnalysisRegistry
import logging

MODELO_PADRAO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

class AgentRevisor:
    def __init__(self):
        self.validator = ParameterValidator()
        self.code_processor = CodeProcessor()
        self.analysis_registry = AnalysisRegistry()
        
    def executar_analise(self, tipo_analise: str,
                         repositorio: Optional[str] = None,
                         codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                         instrucoes_extras: str = "",
                         model_name: str = MODELO_PADRAO_LLM,
                         max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
        try:
            # Validação usando classe especializada
            self.validator.validar_parametros_entrada(
                tipo_analise=tipo_analise, 
                repositorio_nome=repositorio, 
                codigo_entrada=codigo_entrada
            )
            
            # Preparação do código usando classe especializada
            codigo_para_analise = self.code_processor.preparar_codigo_para_analise(
                tipo_analise=tipo_analise, 
                repositorio_nome=repositorio, 
                codigo_entrada=codigo_entrada
            )
            
            if not codigo_para_analise:
                logging.warning('Não foi fornecido nenhum código para análise.')
                return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
            
            codigo_final = self.code_processor.montar_codigo_para_llm(codigo_para_analise)
            
            resultado = executar_analise_llm(
                tipo_analise=tipo_analise,
                codigo=codigo_final,
                analise_extra=instrucoes_extras,
                model_name=model_name,
                max_token_out=max_token_out
            )
            
            return {"tipo_analise": tipo_analise, "resultado": resultado}
            
        except ValueError as ve:
            logging.error(f"Erro de validação: {ve}")
            raise
        except RuntimeError as re:
            logging.error(f"Erro de execução: {re}")
            raise
        except KeyError as ke:
            logging.error(f"Erro de chave: {ke}")
            raise
        except TypeError as te:
            logging.error(f"Erro de tipo: {te}")
            raise

# Instância global para compatibilidade com código existente
_agente_revisor = AgentRevisor()

def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_PADRAO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    """Função de compatibilidade que delega para a instância da classe."""
    return _agente_revisor.executar_analise(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo_entrada=codigo_entrada,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )