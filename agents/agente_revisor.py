from typing import Optional, Dict, Any, Union
from .interfaces import IRepositoryReader, IAnalysisExecutor, IParameterValidator, ICodeProcessor
from .implementations import GitHubRepositoryReader, LLMAnalysisExecutor, ParameterValidator, CodeProcessor
from .error_handlers import CompositeErrorHandler
import logging

# Constantes de configuração
MODELO_PADRAO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000
TIPOS_ANALISE_VALIDOS = ["design", "pentest", "seguranca", "terraform"]

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


class AgenteRevisor:
    """Agente principal responsável pela orquestração da análise de código.
    
    Esta classe implementa o padrão de injeção de dependências e segue os princípios SOLID:
    - SRP: Cada componente tem uma responsabilidade única
    - DIP: Depende de abstrações, não de implementações concretas
    - ISP: Interfaces segregadas por responsabilidade
    """
    
    def __init__(self, 
                 repository_reader: Optional[IRepositoryReader] = None,
                 analysis_executor: Optional[IAnalysisExecutor] = None,
                 parameter_validator: Optional[IParameterValidator] = None,
                 code_processor: Optional[ICodeProcessor] = None):
        """Inicializa o agente com injeção de dependências.
        
        Args:
            repository_reader: Leitor de repositórios (padrão: GitHubRepositoryReader)
            analysis_executor: Executor de análises (padrão: LLMAnalysisExecutor)
            parameter_validator: Validador de parâmetros (padrão: ParameterValidator)
            code_processor: Processador de código (padrão: CodeProcessor)
        """
        # Injeção de dependências com implementações padrão
        self.repository_reader = repository_reader or GitHubRepositoryReader()
        self.analysis_executor = analysis_executor or LLMAnalysisExecutor()
        self.parameter_validator = parameter_validator or ParameterValidator(TIPOS_ANALISE_VALIDOS)
        self.code_processor = code_processor or CodeProcessor(self.repository_reader)
        
        # Manipulador de erros
        self.error_handler = CompositeErrorHandler()
        
        # Logger
        self.logger = logging.getLogger(__name__)
    
    def executar_analise(self, 
                        tipo_analise: str,
                        repositorio: Optional[str] = None,
                        codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                        instrucoes_extras: str = "",
                        model_name: str = MODELO_PADRAO_LLM,
                        max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
        """Executa análise de código seguindo o fluxo completo.
        
        Args:
            tipo_analise: Tipo de análise a ser realizada
            repositorio: Nome do repositório (opcional)
            codigo_entrada: Código de entrada direto (opcional)
            instrucoes_extras: Instruções adicionais para análise
            model_name: Nome do modelo LLM a ser usado
            max_token_out: Máximo de tokens de saída
            
        Returns:
            Dicionário com tipo de análise e resultado
            
        Raises:
            ValueError: Se parâmetros inválidos
            RuntimeError: Se erro na execução
            KeyError: Se erro de chave
            TypeError: Se erro de tipo
        """
        try:
            # 1. Validação de parâmetros
            self._validar_entrada(tipo_analise, repositorio, codigo_entrada)
            
            # 2. Preparação do código
            codigo_preparado = self._preparar_codigo(tipo_analise, repositorio, codigo_entrada)
            
            # 3. Verificação se há código para análise
            if not codigo_preparado:
                self.logger.warning('Não foi fornecido nenhum código para análise.')
                return {
                    "tipo_analise": tipo_analise, 
                    "resultado": 'Não foi fornecido nenhum código para análise'
                }
            
            # 4. Montagem do código para LLM
            codigo_final = self._montar_codigo_llm(codigo_preparado)
            
            # 5. Execução da análise
            resultado = self._executar_analise_llm(
                tipo_analise, codigo_final, instrucoes_extras, model_name, max_token_out
            )
            
            return {
                "tipo_analise": tipo_analise, 
                "resultado": resultado
            }
            
        except (ValueError, RuntimeError, KeyError, TypeError) as e:
            self.error_handler.handle_error(e, "executar_analise")
    
    def _validar_entrada(self, tipo_analise: str, repositorio: Optional[str], 
                        codigo_entrada: Optional[Union[str, Dict[str, str]]]) -> None:
        """Valida parâmetros de entrada."""
        try:
            self.parameter_validator.validar_parametros(tipo_analise, repositorio, codigo_entrada)
        except ValueError as e:
            self.error_handler.handle_error(e, "validação de parâmetros")
    
    def _preparar_codigo(self, tipo_analise: str, repositorio: Optional[str], 
                        codigo_entrada: Optional[Union[str, Dict[str, str]]]) -> Union[str, Dict[str, str]]:
        """Prepara código para análise."""
        try:
            return self.code_processor.preparar_codigo(tipo_analise, repositorio, codigo_entrada)
        except (RuntimeError, KeyError, TypeError) as e:
            self.error_handler.handle_error(e, "preparação de código")
    
    def _montar_codigo_llm(self, codigo_preparado: Union[str, Dict[str, str]]) -> str:
        """Monta código em formato adequado para LLM."""
        try:
            return self.code_processor.montar_codigo_para_llm(codigo_preparado)
        except TypeError as e:
            self.error_handler.handle_error(e, "montagem de código para LLM")
    
    def _executar_analise_llm(self, tipo_analise: str, codigo: str, instrucoes_extras: str, 
                             model_name: str, max_token_out: int) -> str:
        """Executa análise usando LLM."""
        try:
            return self.analysis_executor.executar_analise_llm(
                tipo_analise=tipo_analise,
                codigo=codigo,
                analise_extra=instrucoes_extras,
                model_name=model_name,
                max_token_out=max_token_out
            )
        except RuntimeError as e:
            self.error_handler.handle_error(e, "execução de análise LLM")


# Função de conveniência para manter compatibilidade com a API existente
def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODELO_PADRAO_LLM,
                     max_token_out: int = MAX_TOKENS_SAIDA) -> Dict[str, Any]:
    """Função de conveniência que mantém a interface original.
    
    Esta função cria uma instância do AgenteRevisor e executa a análise,
    mantendo compatibilidade com código existente que usa a função diretamente.
    """
    agente = AgenteRevisor()
    return agente.executar_analise(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo_entrada=codigo_entrada,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )