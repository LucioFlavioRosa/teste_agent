from typing import Optional, Dict, Any, Union
from tools import github_reader
from tools.revisor_geral import executar_analise_llm
import logging

MODELO_PADRAO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000
TIPOS_ANALISE_VALIDOS = ["design", "pentest", "seguranca", "terraform"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def obter_arquivos_codigo_repositorio(repositorio_nome: str, tipo_analise: str) -> Dict[str, str]:
    try:
        logging.info(f'Iniciando a leitura do repositório: {repositorio_nome}')
        arquivos_codigo = github_reader.coletar_arquivos_para_analise(repo_nome=repositorio_nome, tipo_analise=tipo_analise)
        return arquivos_codigo
    except Exception as e:
        tratar_erro_centralizado(e, contexto=f"Falha ao obter código do repositório para análise '{tipo_analise}'")


def validar_parametros(tipo_analise: str, repositorio_nome: Optional[str] = None, codigo_entrada: Optional[Union[str, Dict[str, str]]] = None):
    if tipo_analise not in TIPOS_ANALISE_VALIDOS:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {TIPOS_ANALISE_VALIDOS}")
    if repositorio_nome is None and codigo_entrada is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo_entrada'.")
    return True


def preparar_codigo(tipo_analise: str, repositorio_nome: Optional[str], codigo_entrada: Optional[Union[str, Dict[str, str]]]):
    if codigo_entrada is not None:
        return codigo_entrada
    return obter_arquivos_codigo_repositorio(repositorio_nome=repositorio_nome, tipo_analise=tipo_analise)


def concatenar_codigo_para_llm(codigo_entrada: Union[str, Dict[str, str]]) -> str:
    """
    Concatena o conteúdo dos arquivos se o código for um dicionário, ou retorna a string diretamente.
    """
    if isinstance(codigo_entrada, dict):
        return '\n\n'.join(f"# Arquivo: {k}\n{v}" for k, v in codigo_entrada.items())
    return str(codigo_entrada)


def tratar_erro_centralizado(e: Exception, contexto: str = ""):
    erro_tipo = type(e).__name__
    mensagem = f"Erro ({erro_tipo}) {contexto}: {e}"
    logging.error(mensagem)
    raise


def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_PADRAO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    try:
        validar_parametros(tipo_analise=tipo_analise, repositorio_nome=repositorio, codigo_entrada=codigo_entrada)
        codigo_para_analise = preparar_codigo(tipo_analise=tipo_analise, repositorio_nome=repositorio, codigo_entrada=codigo_entrada)
        if not codigo_para_analise:
            logging.warning('Não foi fornecido nenhum código para análise.')
            return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
        codigo_final = concatenar_codigo_para_llm(codigo_para_analise)
        resultado = executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=codigo_final,
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        return {"tipo_analise": tipo_analise, "resultado": resultado}
    except Exception as e:
        tratar_erro_centralizado(e, contexto="ao executar análise")
