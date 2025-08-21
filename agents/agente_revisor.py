from typing import Optional, Dict, Any
from tools import github_reader
from tools.revisor_geral import executar_analise_llm
import logging

MODELO_PADRAO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000
TIPOS_ANALISE_VALIDOS = ["design", "pentest", "seguranca", "terraform"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def obter_codigo_repositorio(repositorio_nome: str, tipo_analise: str):
    try:
        logging.info(f'Iniciando a leitura do repositório: {repositorio_nome}')
        arquivos_codigo = github_reader.obter_arquivos_para_analise(repo_nome=repositorio_nome, tipo_analise=tipo_analise)
        return arquivos_codigo
    except (ValueError, RuntimeError) as e:
        logging.error(f"Falha ao executar a análise de '{tipo_analise}': {e}")
        raise
    except Exception as e:
        logging.error(f"Erro inesperado ao obter código do repositório: {e}")
        raise

def validar_parametros_entrada(tipo_analise: str, repositorio_nome: Optional[str] = None, codigo: Optional[str] = None):
    if tipo_analise not in TIPOS_ANALISE_VALIDOS:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {TIPOS_ANALISE_VALIDOS}")
    if repositorio_nome is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")
    return True

def preparar_codigo_para_analise(tipo_analise: str, repositorio_nome: Optional[str], codigo: Optional[str]):
    if codigo is not None:
        return codigo
    return obter_codigo_repositorio(repositorio_nome=repositorio_nome, tipo_analise=tipo_analise)

def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo: Optional[str] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_PADRAO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    try:
        validar_parametros_entrada(tipo_analise=tipo_analise, repositorio_nome=repositorio, codigo=codigo)
        codigo_para_analise = preparar_codigo_para_analise(tipo_analise=tipo_analise, repositorio_nome=repositorio, codigo=codigo)
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
    except (KeyError, TypeError) as e:
        logging.error(f"Erro de parâmetro: {e}")
        raise
    except Exception as e:
        logging.error(f"Erro inesperado durante a execução da análise: {e}")
        raise
