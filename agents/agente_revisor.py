from typing import Optional, Dict, Any, Union
from tools import github_reader
from tools.revisor_geral import executar_analise_llm
from services.validador_parametros import ValidadorParametros
from services.preparador_codigo import PreparadorCodigo
from services.montador_codigo import MontadorCodigo
from services.tratador_erros import TratadorErros
from services.registro_tipos_analise import RegistroTiposAnalise
import logging

MODELO_PADRAO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

class AgenteRevisor:
    def __init__(self):
        self.validador = ValidadorParametros()
        self.preparador_codigo = PreparadorCodigo()
        self.montador_codigo = MontadorCodigo()
        self.tratador_erros = TratadorErros()
        self.registro_tipos = RegistroTiposAnalise()
    
    def executar_analise(self, 
                        tipo_analise: str,
                        repositorio: Optional[str] = None,
                        codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                        instrucoes_extras: str = "",
                        model_name: str = MODELO_PADRAO_LLM,
                        max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
        try:
            # Validação de parâmetros
            self.validador.validar_parametros_entrada(
                tipo_analise=tipo_analise, 
                repositorio_nome=repositorio, 
                codigo_entrada=codigo_entrada
            )
            
            # Preparação do código
            codigo_para_analise = self.preparador_codigo.preparar_codigo_para_analise(
                tipo_analise=tipo_analise, 
                repositorio_nome=repositorio, 
                codigo_entrada=codigo_entrada
            )
            
            if not codigo_para_analise:
                logging.warning('Não foi fornecido nenhum código para análise.')
                return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
            
            # Montagem do código para LLM
            codigo_final = self.montador_codigo.montar_codigo_para_llm(codigo_para_analise)
            
            # Execução da análise
            resultado = executar_analise_llm(
                tipo_analise=tipo_analise,
                codigo=codigo_final,
                analise_extra=instrucoes_extras,
                model_name=model_name,
                max_token_out=max_token_out
            )
            
            return {"tipo_analise": tipo_analise, "resultado": resultado}
            
        except (ValueError, RuntimeError, KeyError, TypeError) as e:
            return self.tratador_erros.tratar_erro(e)

# Instância global para compatibilidade com código existente
_agente_revisor = AgenteRevisor()

def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_PADRAO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    """Função de compatibilidade para manter a interface existente"""
    return _agente_revisor.executar_analise(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo_entrada=codigo_entrada,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )