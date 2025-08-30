from typing import Optional, Dict, Any, Union
from tools.github_connector import GitHubConnector
from tools.preenchimento import ValidadorParametros, PreparadorCodigo, TratadorErros
from tools.revisor_geral import executar_analise_llm
import logging

MODELO_PADRAO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Instâncias dos componentes
github_connector = GitHubConnector()
validador = ValidadorParametros()
preparador = PreparadorCodigo(github_connector)
tratador_erros = TratadorErros()

def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_PADRAO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    """Executa análise de código usando LLM.
    
    Args:
        tipo_analise: Tipo de análise a ser executada
        repositorio: Nome do repositório (opcional)
        codigo_entrada: Código para análise (opcional)
        instrucoes_extras: Instruções adicionais para a análise
        model_name: Nome do modelo LLM a ser usado
        max_token_out: Máximo de tokens na saída
        
    Returns:
        Dict[str, Any]: Resultado da análise
    """
    try:
        # Validação de parâmetros
        validador.validar_parametros_entrada(
            tipo_analise=tipo_analise, 
            repositorio_nome=repositorio, 
            codigo_entrada=codigo_entrada
        )
        
        # Preparação do código
        codigo_para_analise = preparador.preparar_codigo_para_analise(
            tipo_analise=tipo_analise, 
            repositorio_nome=repositorio, 
            codigo_entrada=codigo_entrada
        )
        
        if not codigo_para_analise:
            logging.warning('Não foi fornecido nenhum código para análise.')
            return {
                "tipo_analise": tipo_analise, 
                "resultado": 'Não foi fornecido nenhum código para análise'
            }
        
        # Montagem do código para LLM
        codigo_final = preparador.montar_codigo_para_llm(codigo_para_analise)
        
        # Execução da análise
        resultado = executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=codigo_final,
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        
        return {"tipo_analise": tipo_analise, "resultado": resultado}
        
    except ValueError as ve:
        tratador_erros.tratar_erro_validacao(ve)
    except RuntimeError as re:
        tratador_erros.tratar_erro_execucao(re)
    except KeyError as ke:
        tratador_erros.tratar_erro_chave(ke)
    except TypeError as te:
        tratador_erros.tratar_erro_tipo(te)
