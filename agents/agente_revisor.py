from typing import Optional, Dict, Any, Union
from agents.validators import ParameterValidator
from agents.code_assembler import CodeAssembler
from agents.analysis_executor import AnalysisExecutor
from agents.error_handler import ErrorHandler
import logging

MODELO_PADRAO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_PADRAO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    """
    Função principal para executar análise de código.
    Orquestra as diferentes responsabilidades através de módulos especializados.
    """
    try:
        # Validação de parâmetros
        validator = ParameterValidator()
        validator.validate(tipo_analise, repositorio, codigo_entrada)
        
        # Montagem do código para análise
        assembler = CodeAssembler()
        codigo_para_analise = assembler.prepare_code(tipo_analise, repositorio, codigo_entrada)
        
        if not codigo_para_analise:
            logging.warning('Não foi fornecido nenhum código para análise.')
            return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
        
        codigo_final = assembler.assemble_for_llm(codigo_para_analise)
        
        # Execução da análise
        executor = AnalysisExecutor()
        resultado = executor.execute(
            tipo_analise=tipo_analise,
            codigo=codigo_final,
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        
        return {"tipo_analise": tipo_analise, "resultado": resultado}
        
    except (ValueError, RuntimeError, KeyError, TypeError) as e:
        error_handler = ErrorHandler()
        error_handler.handle_error(e)
