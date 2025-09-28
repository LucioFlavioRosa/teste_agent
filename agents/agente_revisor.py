from typing import Optional, Dict, Any, Union
from tools import github_reader
from tools.revisor_geral import executar_analise_llm
from agents.validators.parameter_validator import ParameterValidator
from agents.processors.code_processor import CodeProcessor
from agents.handlers.error_handler import ErrorHandler
import logging

MODELO_PADRAO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000
TIPOS_ANALISE_VALIDOS = ["design", "pentest", "seguranca", "terraform"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

class AgentRevisor:
    def __init__(self):
        self.validator = ParameterValidator(TIPOS_ANALISE_VALIDOS)
        self.processor = CodeProcessor()
        self.error_handler = ErrorHandler()
    
    def executar_analise(self, tipo_analise: str,
                        repositorio: Optional[str] = None,
                        codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                        instrucoes_extras: str = "",
                        model_name: str = MODELO_PADRAO_LLM,
                        max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
        try:
            self.validator.validar_parametros_entrada(tipo_analise, repositorio, codigo_entrada)
            codigo_para_analise = self.processor.preparar_codigo_para_analise(tipo_analise, repositorio, codigo_entrada)
            
            if not codigo_para_analise:
                logging.warning('Não foi fornecido nenhum código para análise.')
                return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
            
            codigo_final = self.processor.montar_codigo_para_llm(codigo_para_analise)
            resultado = executar_analise_llm(
                tipo_analise=tipo_analise,
                codigo=codigo_final,
                analise_extra=instrucoes_extras,
                model_name=model_name,
                max_token_out=max_token_out
            )
            return {"tipo_analise": tipo_analise, "resultado": resultado}
        except (ValueError, RuntimeError, KeyError, TypeError) as e:
            self.error_handler.tratar_erro(e)

_agente_revisor_instance = AgentRevisor()

def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_PADRAO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    return _agente_revisor_instance.executar_analise(
        tipo_analise, repositorio, codigo_entrada, instrucoes_extras, model_name, max_token_out
    )