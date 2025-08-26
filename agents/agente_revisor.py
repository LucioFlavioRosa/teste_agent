from typing import Optional, Dict, Any, Union
from tools import github_reader
from tools.revisor_geral import executar_analise_llm
import logging

MODELO_PADRAO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000
TIPOS_ANALISE_VALIDOS = ["design", "pentest", "seguranca", "terraform"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def obter_codigo_repositorio(repositorio_nome: str, tipo_analise: str) -> Dict[str, str]:
    try:
        logging.info(f'Iniciando a leitura do repositório: {repositorio_nome}')
        arquivos_codigo = github_reader.obter_arquivos_para_analise(repo_nome=repositorio_nome, tipo_analise=tipo_analise)
        return arquivos_codigo
    except (ValueError, RuntimeError) as e:
        logging.error(f"Falha ao executar a análise de '{tipo_analise}': {e}")
        raise
    except KeyError as e:
        logging.error(f"Erro de chave ao obter código do repositório: {e}")
        raise
    except TypeError as e:
        logging.error(f"Erro de tipo ao obter código do repositório: {e}")
        raise

def validar_parametros_entrada(tipo_analise: str, repositorio_nome: Optional[str] = None, codigo_entrada: Optional[Union[str, Dict[str, str]]] = None):
    if tipo_analise not in TIPOS_ANALISE_VALIDOS:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {TIPOS_ANALISE_VALIDOS}")
    if repositorio_nome is None and codigo_entrada is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo_entrada'.")
    return True

def preparar_codigo_para_analise(tipo_analise: str, repositorio_nome: Optional[str], codigo_entrada: Optional[Union[str, Dict[str, str]]]):
    if codigo_entrada is not None:
        return codigo_entrada
    return obter_codigo_repositorio(repositorio_nome=repositorio_nome, tipo_analise=tipo_analise)

def montar_codigo_para_llm(codigo_entrada: Union[str, Dict[str, str]]) -> str:
    """
    Concatena o conteúdo dos arquivos se o código for um dicionário, ou retorna a string diretamente.
    """
    if isinstance(codigo_entrada, dict):
        return '\n\n'.join(f"# Arquivo: {k}\n{v}" for k, v in codigo_entrada.items())
    return str(codigo_entrada)

def tratar_erro_validacao(ve: Exception):
    logging.error(f"Erro de validação: {ve}")
    raise

def tratar_erro_execucao(re: Exception):
    logging.error(f"Erro de execução: {re}")
    raise

def tratar_erro_chave(ke: Exception):
    logging.error(f"Erro de chave: {ke}")
    raise

def tratar_erro_tipo(te: Exception):
    logging.error(f"Erro de tipo: {te}")
    raise

def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_PADRAO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    """
    Executa a análise do código fornecido ou do repositório especificado, utilizando o modelo LLM.

    Parâmetros:
        tipo_analise (str): Tipo de análise a ser realizada ('design', 'pentest', 'seguranca', 'terraform').
        repositorio (str, opcional): Nome do repositório GitHub a ser analisado.
        codigo_entrada (str ou dict, opcional): Código fonte a ser analisado.
        instrucoes_extras (str): Instruções adicionais do usuário para a análise.
        model_name (str): Nome do modelo LLM a ser utilizado.
        max_token_out (int): Número máximo de tokens na resposta.

    Retorno:
        dict: Resultado da análise.
    """
    try:
        validar_parametros_entrada(tipo_analise=tipo_analise, repositorio_nome=repositorio, codigo_entrada=codigo_entrada)
        codigo_para_analise = preparar_codigo_para_analise(tipo_analise=tipo_analise, repositorio_nome=repositorio, codigo_entrada=codigo_entrada)
        if not codigo_para_analise:
            logging.warning('Não foi fornecido nenhum código para análise.')
            return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
        codigo_final = montar_codigo_para_llm(codigo_para_analise)
        resultado = executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=codigo_final,
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        return {"tipo_analise": tipo_analise, "resultado": resultado}
    except ValueError as ve:
        tratar_erro_validacao(ve)
    except RuntimeError as re:
        tratar_erro_execucao(re)
    except KeyError as ke:
        tratar_erro_chave(ke)
    except TypeError as te:
        tratar_erro_tipo(te)
