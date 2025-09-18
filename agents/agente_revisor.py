from typing import Optional, Dict, Any, Union
import logging
from services.openai_llm_service import OpenAILLMService
from services.analysis_registry import DefaultAnalysisRegistry
from services.github_repository import GitHubRepository
from services.prompt_loader import PromptLoader
from validators.parameter_validator import ParameterValidator
from processors.code_processor import CodeProcessor
from interfaces.llm_service import LLMService, AnalysisTypeRegistry, CodeRepository

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

MODELO_PADRAO_LLM = 'gpt-4.1'
MAX_TOKENS_SAIDA = 3000

class AgenteRevisor:
    """Agente principal para execução de análises de código"""
    
    def __init__(
        self,
        llm_service: LLMService = None,
        registry: AnalysisTypeRegistry = None,
        repository: CodeRepository = None,
        prompt_loader: PromptLoader = None
    ):
        # Injeção de dependências com fallback para implementações padrão
        self.llm_service = llm_service or OpenAILLMService()
        self.registry = registry or DefaultAnalysisRegistry()
        self.repository = repository or GitHubRepository()
        self.prompt_loader = prompt_loader or PromptLoader()
        
        # Inicialização de componentes dependentes
        self.validator = ParameterValidator(self.registry.tipos_validos())
        self.code_processor = CodeProcessor(self.repository, self.registry)
    
    def executar_analise(
        self,
        tipo_analise: str,
        repositorio: Optional[str] = None,
        codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
        instrucoes_extras: str = "",
        model_name: str = MODELO_PADRAO_LLM,
        max_token_out: int = MAX_TOKENS_SAIDA
    ) -> Dict[str, Any]:
        """Executa análise de código seguindo os princípios SOLID"""
        try:
            # Validação de parâmetros
            self.validator.validar_parametros_analise(
                tipo_analise=tipo_analise,
                repositorio_nome=repositorio,
                codigo_entrada=codigo_entrada
            )
            
            # Preparação do código
            codigo_para_analise = self.code_processor.preparar_codigo_para_analise(
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
            codigo_final = self.code_processor.montar_codigo_para_llm(codigo_para_analise)
            
            # Carregamento do prompt
            prompt_sistema = self.prompt_loader.carregar_prompt(tipo_analise)
            
            # Execução da análise
            resultado = self.llm_service.executar_analise(
                prompt_sistema=prompt_sistema,
                codigo=codigo_final,
                instrucoes_extras=instrucoes_extras,
                model_name=model_name,
                max_tokens=max_token_out
            )
            
            logging.info(f"Análise '{tipo_analise}' executada com sucesso")
            return {
                "tipo_analise": tipo_analise,
                "resultado": resultado
            }
            
        except ValueError as ve:
            logging.error(f"Erro de validação: {ve}")
            raise
        except RuntimeError as re:
            logging.error(f"Erro de execução: {re}")
            raise
        except Exception as e:
            logging.error(f"Erro inesperado: {e}")
            raise RuntimeError(f"Erro inesperado na análise: {e}") from e

# Instância global para compatibilidade com código existente
_agente_global = AgenteRevisor()

# Funções de compatibilidade
def executar_analise(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo_entrada: Optional[Union[str, Dict[str, str]]] = None,
    instrucoes_extras: str = "",
    model_name: str = MODELO_PADRAO_LLM,
    max_token_out: int = MAX_TOKENS_SAIDA
) -> Dict[str, Any]:
    """Função de compatibilidade que usa a instância global"""
    return _agente_global.executar_analise(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo_entrada=codigo_entrada,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )