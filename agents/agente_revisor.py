from typing import Optional, Dict, Any, Union
from tools import github_reader
from tools.revisor_geral import executar_analise_llm
import logging

MODELO_PADRAO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000
TIPOS_ANALISE_VALIDOS = ["design", "pentest", "seguranca", "terraform"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

class ValidadorParametros:
    @staticmethod
    def validar(tipo_analise: str, repositorio_nome: Optional[str] = None, codigo_entrada: Optional[Union[str, Dict[str, str]]] = None):
        if tipo_analise not in TIPOS_ANALISE_VALIDOS:
            raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {TIPOS_ANALISE_VALIDOS}")
        if repositorio_nome is None and codigo_entrada is None:
            raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo_entrada'.")
        return True

class PreparadorCodigo:
    @staticmethod
    def preparar(tipo_analise: str, repositorio_nome: Optional[str], codigo_entrada: Optional[Union[str, Dict[str, str]]]):
        if codigo_entrada is not None:
            return codigo_entrada
        return PreparadorCodigo._obter_codigo_repositorio(repositorio_nome, tipo_analise)
    
    @staticmethod
    def _obter_codigo_repositorio(repositorio_nome: str, tipo_analise: str) -> Dict[str, str]:
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

class MontadorCodigo:
    @staticmethod
    def montar_para_llm(codigo_entrada: Union[str, Dict[str, str]]) -> str:
        if isinstance(codigo_entrada, dict):
            return '\n\n'.join(f"# Arquivo: {k}\n{v}" for k, v in codigo_entrada.items())
        return str(codigo_entrada)

class TratadorErros:
    @staticmethod
    def tratar_erro_validacao(ve: Exception):
        logging.error(f"Erro de validação: {ve}")
        raise
    
    @staticmethod
    def tratar_erro_execucao(re: Exception):
        logging.error(f"Erro de execução: {re}")
        raise
    
    @staticmethod
    def tratar_erro_chave(ke: Exception):
        logging.error(f"Erro de chave: {ke}")
        raise
    
    @staticmethod
    def tratar_erro_tipo(te: Exception):
        logging.error(f"Erro de tipo: {te}")
        raise

class ExecutorAnalise:
    def __init__(self):
        self.validador = ValidadorParametros()
        self.preparador = PreparadorCodigo()
        self.montador = MontadorCodigo()
        self.tratador_erros = TratadorErros()
    
    def executar(self, tipo_analise: str,
                 repositorio: Optional[str] = None,
                 codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                 instrucoes_extras: str = "",
                 model_name: str = MODELO_PADRAO_LLM,
                 max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
        try:
            self.validador.validar(tipo_analise=tipo_analise, repositorio_nome=repositorio, codigo_entrada=codigo_entrada)
            codigo_para_analise = self.preparador.preparar(tipo_analise=tipo_analise, repositorio_nome=repositorio, codigo_entrada=codigo_entrada)
            
            if not codigo_para_analise:
                logging.warning('Não foi fornecido nenhum código para análise.')
                return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
            
            codigo_final = self.montador.montar_para_llm(codigo_para_analise)
            resultado = executar_analise_llm(
                tipo_analise=tipo_analise,
                codigo=codigo_final,
                analise_extra=instrucoes_extras,
                model_name=model_name,
                max_token_out=max_token_out
            )
            return {"tipo_analise": tipo_analise, "resultado": resultado}
        except ValueError as ve:
            self.tratador_erros.tratar_erro_validacao(ve)
        except RuntimeError as re:
            self.tratador_erros.tratar_erro_execucao(re)
        except KeyError as ke:
            self.tratador_erros.tratar_erro_chave(ke)
        except TypeError as te:
            self.tratador_erros.tratar_erro_tipo(te)

_executor_global = ExecutorAnalise()

def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_PADRAO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    return _executor_global.executar(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo_entrada=codigo_entrada,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )