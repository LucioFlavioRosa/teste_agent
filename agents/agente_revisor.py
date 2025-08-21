from typing import Optional, Dict, Any, Union
from tools import github_reader
from tools.revisor_geral import executar_analise_llm
import logging

MODELO_PADRAO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000
TIPOS_ANALISE_VALIDOS = ["design", "pentest", "seguranca", "terraform"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def obter_arquivos_do_repositorio_para_analise(nome_repositorio: str, tipo_analise: str) -> Dict[str, str]:
    try:
        logging.info(f'Iniciando a leitura do repositório: {nome_repositorio}')
        arquivos_codigo = github_reader.obter_arquivos_para_analise(repo_nome=nome_repositorio, tipo_analise=tipo_analise)
        return arquivos_codigo
    except (ValueError, RuntimeError) as erro:
        logging.error(f"Falha ao executar a análise de '{tipo_analise}': {erro}")
        raise
    except KeyError as erro:
        logging.error(f"Erro de chave ao obter código do repositório: {erro}")
        raise
    except TypeError as erro:
        logging.error(f"Erro de tipo ao obter código do repositório: {erro}")
        raise

def validar_parametros_de_entrada(tipo_analise: str, nome_repositorio: Optional[str] = None, codigo_entrada: Optional[Union[str, Dict[str, str]]] = None):
    if tipo_analise not in TIPOS_ANALISE_VALIDOS:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {TIPOS_ANALISE_VALIDOS}")
    if nome_repositorio is None and codigo_entrada is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo_entrada'.")
    return True

def preparar_codigo_para_analise(tipo_analise: str, nome_repositorio: Optional[str], codigo_entrada: Optional[Union[str, Dict[str, str]]]):
    if codigo_entrada is not None:
        return codigo_entrada
    return obter_arquivos_do_repositorio_para_analise(nome_repositorio=nome_repositorio, tipo_analise=tipo_analise)

def montar_codigo_para_envio_llm(codigo_entrada: Union[str, Dict[str, str]]) -> str:
    """
    Concatena o conteúdo dos arquivos se o código for um dicionário, ou retorna a string diretamente.
    """
    if isinstance(codigo_entrada, dict):
        return '\n\n'.join(f"# Arquivo: {caminho}\n{conteudo}" for caminho, conteudo in codigo_entrada.items())
    return str(codigo_entrada)

def tratar_erro_validacao(erro: Exception):
    logging.error(f"Erro de validação: {erro}")
    raise

def tratar_erro_execucao(erro: Exception):
    logging.error(f"Erro de execução: {erro}")
    raise

def tratar_erro_chave(erro: Exception):
    logging.error(f"Erro de chave: {erro}")
    raise

def tratar_erro_tipo(erro: Exception):
    logging.error(f"Erro de tipo: {erro}")
    raise

def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_PADRAO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    """
    Executa a análise dividindo responsabilidades em funções menores e usando nomes claros.
    """
    try:
        validar_parametros_de_entrada(tipo_analise=tipo_analise, nome_repositorio=repositorio, codigo_entrada=codigo_entrada)
        codigo_para_analise = preparar_codigo_para_analise(tipo_analise=tipo_analise, nome_repositorio=repositorio, codigo_entrada=codigo_entrada)
        if not codigo_para_analise:
            logging.warning('Não foi fornecido nenhum código para análise.')
            return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
        codigo_final = montar_codigo_para_envio_llm(codigo_para_analise)
        resultado = executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=codigo_final,
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        return {"tipo_analise": tipo_analise, "resultado": resultado}
    except ValueError as erro:
        tratar_erro_validacao(erro)
    except RuntimeError as erro:
        tratar_erro_execucao(erro)
    except KeyError as erro:
        tratar_erro_chave(erro)
    except TypeError as erro:
        tratar_erro_tipo(erro)
