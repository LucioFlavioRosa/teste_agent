from typing import Optional, Dict, Any, Union
from tools import github_reader
from tools.revisor_geral import executar_analise_llm
import logging

MODELO_PADRAO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000
TIPOS_ANALISE_VALIDOS = ["design", "pentest", "seguranca", "terraform"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


class ValidadorParametros:
    """Responsável pela validação de parâmetros de entrada."""
    
    def __init__(self, tipos_validos: list):
        self.tipos_validos = tipos_validos
    
    def validar(self, tipo_analise: str, repositorio_nome: Optional[str] = None, 
               codigo_entrada: Optional[Union[str, Dict[str, str]]] = None) -> bool:
        """Valida os parâmetros de entrada da análise."""
        if tipo_analise not in self.tipos_validos:
            raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {self.tipos_validos}")
        
        if repositorio_nome is None and codigo_entrada is None:
            raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo_entrada'.")
        
        return True


class ObtenedorCodigo:
    """Responsável pela obtenção e preparação do código para análise."""
    
    def obter_codigo_repositorio(self, repositorio_nome: str, tipo_analise: str) -> Dict[str, str]:
        """Obtém código do repositório GitHub."""
        try:
            logging.info(f'Iniciando a leitura do repositório: {repositorio_nome}')
            arquivos_codigo = github_reader.obter_arquivos_para_analise(
                repo_nome=repositorio_nome, 
                tipo_analise=tipo_analise
            )
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
    
    def preparar_codigo(self, tipo_analise: str, repositorio_nome: Optional[str], 
                       codigo_entrada: Optional[Union[str, Dict[str, str]]]) -> Union[str, Dict[str, str]]:
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
    """Responsável pelo tratamento centralizado de erros."""
    
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


class OrquestradorAnalise:
    """Responsável pela orquestração do processo de análise."""
    
    def __init__(self):
        self.validador = ValidadorParametros(TIPOS_ANALISE_VALIDOS)
        self.obtenedor_codigo = ObtenedorCodigo()
        self.tratador_erros = TratadorErros()
    
    def executar(self, tipo_analise: str,
                repositorio: Optional[str] = None,
                codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                instrucoes_extras: str = "",
                model_name: str = MODELO_PADRAO_LLM,
                max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
        """Executa a análise completa do código."""
        try:
            # Validação de parâmetros
            self.validador.validar(
                tipo_analise=tipo_analise, 
                repositorio_nome=repositorio, 
                codigo_entrada=codigo_entrada
            )
            
            # Preparação do código
            codigo_para_analise = self.obtenedor_codigo.preparar_codigo(
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
            codigo_final = self.obtenedor_codigo.montar_codigo_para_llm(codigo_para_analise)
            
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
            self.tratador_erros.tratar_erro_validacao(ve)
        except RuntimeError as re:
            self.tratador_erros.tratar_erro_execucao(re)
        except KeyError as ke:
            self.tratador_erros.tratar_erro_chave(ke)
        except TypeError as te:
            self.tratador_erros.tratar_erro_tipo(te)


# Instância global do orquestrador para manter compatibilidade com a API existente
_orquestrador = OrquestradorAnalise()


def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_PADRAO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    """Função de conveniência que mantém a interface original para compatibilidade."""
    return _orquestrador.executar(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo_entrada=codigo_entrada,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )