from typing import Optional, Dict, Any
from tools import github_reader
from tools.revisor_geral import executar_analise_llm
import logging

modelo_llm = 'gpt-4.1'
max_tokens_saida = 3000

analises_validas = ["design", "pentest", "seguranca", "terraform"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def obter_codigo_do_repositorio(repositorio: str, tipo_analise: str):
    try:
        logging.info(f'Iniciando a leitura do repositório: {repositorio}')
        codigo_para_analise = github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo_para_analise
    except (ValueError, RuntimeError) as e:
        logging.error(f"Falha ao executar a análise de '{tipo_analise}': {e}")
        raise
    except Exception as e:
        logging.exception(f"Erro inesperado ao obter código do repositório: {e}")
        raise

def validar_parametros(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None):
    if tipo_analise not in analises_validas:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {analises_validas}")
    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")
    return True

def preparar_codigo_para_analise(tipo_analise: str, repositorio: Optional[str], codigo: Optional[str]):
    if codigo is not None:
        return codigo
    return obter_codigo_do_repositorio(repositorio=repositorio, tipo_analise=tipo_analise)

def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo: Optional[str] = None,
                     instrucoes_extras: str = "",
                     model_name: str = modelo_llm,
                     max_token_out: int = max_tokens_saida) -> Dict[str, Any]:
    try:
        validar_parametros(tipo_analise=tipo_analise, repositorio=repositorio, codigo=codigo)
        codigo_para_analise = preparar_codigo_para_analise(tipo_analise=tipo_analise, repositorio=repositorio, codigo=codigo)
        if not codigo_para_analise:
            logging.warning('Não foi fornecido nenhum código para análise.')
            return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
        resultado = executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=str(codigo_para_analise),
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
    except Exception as e:
        logging.exception(f"Erro inesperado durante a execução da análise: {e}")
        raise