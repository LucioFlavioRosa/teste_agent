from typing import Optional, Dict, Any, Union
from tools import github_reader
from tools.revisor_geral import executar_analise_llm
import logging
from abc import ABC, abstractmethod

MODELO_PADRAO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


class ValidadorParametros:
    """Classe responsável pela validação de parâmetros de entrada."""
    
    def __init__(self):
        self._tipos_analise_validos = ["design", "pentest", "seguranca", "terraform"]
    
    def validar_parametros_entrada(self, tipo_analise: str, repositorio_nome: Optional[str] = None, codigo_entrada: Optional[Union[str, Dict[str, str]]] = None) -> bool:
        """Valida os parâmetros de entrada para a análise."""
        if tipo_analise not in self._tipos_analise_validos:
            raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {self._tipos_analise_validos}")
        if repositorio_nome is None and codigo_entrada is None:
            raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo_entrada'.")
        return True
    
    def adicionar_tipo_analise(self, novo_tipo: str) -> None:
        """Permite adicionar novos tipos de análise dinamicamente."""
        if novo_tipo not in self._tipos_analise_validos:
            self._tipos_analise_validos.append(novo_tipo)
            logging.info(f"Novo tipo de análise adicionado: {novo_tipo}")
    
    def obter_tipos_validos(self) -> list:
        """Retorna a lista de tipos de análise válidos."""
        return self._tipos_analise_validos.copy()


class PreparadorCodigo:
    """Classe responsável pela preparação e montagem do código para análise."""
    
    def obter_codigo_repositorio(self, repositorio_nome: str, tipo_analise: str) -> Dict[str, str]:
        """Obtém o código do repositório GitHub."""
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
    
    def preparar_codigo_para_analise(self, tipo_analise: str, repositorio_nome: Optional[str], codigo_entrada: Optional[Union[str, Dict[str, str]]]) -> Union[str, Dict[str, str]]:
        """Prepara o código para análise, seja do repositório ou entrada direta."""
        if codigo_entrada is not None:
            return codigo_entrada
        return self.obter_codigo_repositorio(repositorio_nome=repositorio_nome, tipo_analise=tipo_analise)
    
    def montar_codigo_para_llm(self, codigo_entrada: Union[str, Dict[str, str]]) -> str:
        """Concatena o conteúdo dos arquivos se o código for um dicionário, ou retorna a string diretamente."""
        if isinstance(codigo_entrada, dict):
            return '\n\n'.join(f"# Arquivo: {k}\n{v}" for k, v in codigo_entrada.items())
        return str(codigo_entrada)


class TratadorErros:
    """Classe responsável pelo tratamento centralizado de erros."""
    
    def tratar_erro_validacao(self, ve: Exception) -> None:
        """Trata erros de validação."""
        logging.error(f"Erro de validação: {ve}")
        raise
    
    def tratar_erro_execucao(self, re: Exception) -> None:
        """Trata erros de execução."""
        logging.error(f"Erro de execução: {re}")
        raise
    
    def tratar_erro_chave(self, ke: Exception) -> None:
        """Trata erros de chave."""
        logging.error(f"Erro de chave: {ke}")
        raise
    
    def tratar_erro_tipo(self, te: Exception) -> None:
        """Trata erros de tipo."""
        logging.error(f"Erro de tipo: {te}")
        raise


class ExecutorAnalise:
    """Classe principal responsável pela orquestração da análise."""
    
    def __init__(self):
        self.validador = ValidadorParametros()
        self.preparador_codigo = PreparadorCodigo()
        self.tratador_erros = TratadorErros()
    
    def executar_analise(self,
                        tipo_analise: str,
                        repositorio: Optional[str] = None,
                        codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                        instrucoes_extras: str = "",
                        model_name: str = MODELO_PADRAO_LLM,
                        max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
        """Executa a análise completa do código."""
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
            
            # Montagem do código para o LLM
            codigo_final = self.preparador_codigo.montar_codigo_para_llm(codigo_para_analise)
            
            # Execução da análise via LLM
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


# Instância global para manter compatibilidade com a API existente
_executor_global = ExecutorAnalise()

# Funções de compatibilidade para manter a interface existente
def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_PADRAO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    """Função de compatibilidade que mantém a interface original."""
    return _executor_global.executar_analise(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo_entrada=codigo_entrada,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )


# Funções auxiliares para acesso às funcionalidades específicas
def obter_codigo_repositorio(repositorio_nome: str, tipo_analise: str) -> Dict[str, str]:
    """Função de compatibilidade para obter código do repositório."""
    return _executor_global.preparador_codigo.obter_codigo_repositorio(repositorio_nome, tipo_analise)

def validar_parametros_entrada(tipo_analise: str, repositorio_nome: Optional[str] = None, codigo_entrada: Optional[Union[str, Dict[str, str]]] = None):
    """Função de compatibilidade para validação de parâmetros."""
    return _executor_global.validador.validar_parametros_entrada(tipo_analise, repositorio_nome, codigo_entrada)

def preparar_codigo_para_analise(tipo_analise: str, repositorio_nome: Optional[str], codigo_entrada: Optional[Union[str, Dict[str, str]]]):
    """Função de compatibilidade para preparação de código."""
    return _executor_global.preparador_codigo.preparar_codigo_para_analise(tipo_analise, repositorio_nome, codigo_entrada)

def montar_codigo_para_llm(codigo_entrada: Union[str, Dict[str, str]]) -> str:
    """Função de compatibilidade para montagem de código."""
    return _executor_global.preparador_codigo.montar_codigo_para_llm(codigo_entrada)

# Funções de tratamento de erro (mantidas para compatibilidade)
def tratar_erro_validacao(ve: Exception):
    return _executor_global.tratador_erros.tratar_erro_validacao(ve)

def tratar_erro_execucao(re: Exception):
    return _executor_global.tratador_erros.tratar_erro_execucao(re)

def tratar_erro_chave(ke: Exception):
    return _executor_global.tratador_erros.tratar_erro_chave(ke)

def tratar_erro_tipo(te: Exception):
    return _executor_global.tratador_erros.tratar_erro_tipo(te)