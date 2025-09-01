from typing import Optional, Dict, Any, Union
from tools.github_connector import GitHubConnector, ColabConfigProvider
from tools.preenchimento import PreenchimentoCodigo
from tools.revisor_geral import executar_analise_llm
import logging

MODELO_PADRAO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000
TIPOS_ANALISE_VALIDOS = ["design", "pentest", "seguranca", "terraform"]

# Mapeamento de tipos de análise para extensões de arquivo
TIPO_EXTENSOES_MAPEAMENTO = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"],
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

class ValidadorParametros:
    """
    Classe responsável pela validação de parâmetros de entrada.
    Segue o Princípio da Responsabilidade Única (SRP).
    """
    
    @staticmethod
    def validar_parametros_entrada(tipo_analise: str, 
                                 repositorio_nome: Optional[str] = None, 
                                 codigo_entrada: Optional[Union[str, Dict[str, str]]] = None):
        """
        Valida os parâmetros de entrada para análise.
        
        Args:
            tipo_analise: Tipo de análise a ser executada
            repositorio_nome: Nome do repositório (opcional)
            codigo_entrada: Código fornecido diretamente (opcional)
            
        Raises:
            ValueError: Se os parâmetros são inválidos
        """
        if tipo_analise not in TIPOS_ANALISE_VALIDOS:
            raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {TIPOS_ANALISE_VALIDOS}")
        
        if repositorio_nome is None and codigo_entrada is None:
            raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo_entrada'.")
        
        return True

class TratadorErros:
    """
    Classe responsável pelo tratamento centralizado de erros.
    Segue o Princípio da Responsabilidade Única (SRP).
    """
    
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
    """
    Classe principal responsável pela orquestração da análise.
    Utiliza injeção de dependência e segue o SRP.
    """
    
    def __init__(self, github_connector: GitHubConnector = None):
        """
        Inicializa o orquestrador com suas dependências.
        
        Args:
            github_connector: Conector para GitHub (opcional, usa padrão se None)
        """
        self.github_connector = github_connector or GitHubConnector(ColabConfigProvider())
        self.validador = ValidadorParametros()
        self.preenchimento = PreenchimentoCodigo()
        self.tratador_erros = TratadorErros()
    
    def obter_codigo_repositorio(self, repositorio_nome: str, tipo_analise: str) -> Dict[str, str]:
        """
        Obtém código do repositório para análise.
        
        Args:
            repositorio_nome: Nome do repositório
            tipo_analise: Tipo de análise
            
        Returns:
            Dict[str, str]: Arquivos do repositório
        """
        try:
            logging.info(f'Iniciando a leitura do repositório: {repositorio_nome}')
            extensoes_alvo = TIPO_EXTENSOES_MAPEAMENTO.get(tipo_analise.lower())
            arquivos_codigo = self.github_connector.obter_arquivos_por_extensoes(
                repositorio_nome=repositorio_nome, 
                extensoes_alvo=extensoes_alvo
            )
            return arquivos_codigo
        except Exception as e:
            logging.error(f"Falha ao executar a análise de '{tipo_analise}': {e}")
            raise
    
    def executar_analise(self, 
                        tipo_analise: str,
                        repositorio: Optional[str] = None,
                        codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                        instrucoes_extras: str = "",
                        model_name: str = MODELO_PADRAO_LLM,
                        max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
        """
        Executa a análise completa seguindo o fluxo orquestrado.
        
        Args:
            tipo_analise: Tipo de análise a executar
            repositorio: Nome do repositório (opcional)
            codigo_entrada: Código fornecido diretamente (opcional)
            instrucoes_extras: Instruções adicionais
            model_name: Nome do modelo LLM
            max_token_out: Máximo de tokens de saída
            
        Returns:
            Dict[str, Any]: Resultado da análise
        """
        try:
            # Validação de parâmetros
            self.validador.validar_parametros_entrada(
                tipo_analise=tipo_analise, 
                repositorio_nome=repositorio, 
                codigo_entrada=codigo_entrada
            )
            
            # Preparação do código
            codigo_para_analise = self.preenchimento.preparar_codigo_para_analise(
                codigo_entrada=codigo_entrada,
                obter_codigo_callback=self.obter_codigo_repositorio,
                repositorio_nome=repositorio,
                tipo_analise=tipo_analise
            )
            
            # Validação de código disponível
            if not self.preenchimento.validar_codigo_disponivel(codigo_para_analise):
                logging.warning('Não foi fornecido nenhum código para análise.')
                return {
                    "tipo_analise": tipo_analise, 
                    "resultado": 'Não foi fornecido nenhum código para análise'
                }
            
            # Montagem do código para LLM
            codigo_final = self.preenchimento.montar_codigo_para_llm(codigo_para_analise)
            
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

# Instância global para manter compatibilidade com código existente
_orquestrador_global = OrquestradorAnalise()

# Funções de compatibilidade para manter a API existente
def executar_analise(tipo_analise: str,
                    repositorio: Optional[str] = None,
                    codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                    instrucoes_extras: str = "",
                    model_name: str = MODELO_PADRAO_LLM,
                    max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    """
    Função de compatibilidade que delega para o orquestrador global.
    """
    return _orquestrador_global.executar_analise(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo_entrada=codigo_entrada,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )