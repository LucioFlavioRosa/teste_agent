from abc import ABC, abstractmethod
from typing import Dict, Any, Union, Optional


class IRepositoryReader(ABC):
    """Interface para leitura de repositórios."""
    
    @abstractmethod
    def obter_arquivos_para_analise(self, repo_nome: str, tipo_analise: str) -> Dict[str, str]:
        """Obtém arquivos do repositório para análise.
        
        Args:
            repo_nome: Nome do repositório
            tipo_analise: Tipo de análise a ser realizada
            
        Returns:
            Dicionário com arquivos e seus conteúdos
            
        Raises:
            ValueError: Se parâmetros inválidos
            RuntimeError: Se erro na leitura do repositório
        """
        pass


class IAnalysisExecutor(ABC):
    """Interface para execução de análises LLM."""
    
    @abstractmethod
    def executar_analise_llm(self, tipo_analise: str, codigo: str, 
                           analise_extra: str = "", model_name: str = "gpt-4.1", 
                           max_token_out: int = 3000) -> str:
        """Executa análise usando LLM.
        
        Args:
            tipo_analise: Tipo de análise
            codigo: Código a ser analisado
            analise_extra: Instruções extras
            model_name: Nome do modelo LLM
            max_token_out: Máximo de tokens de saída
            
        Returns:
            Resultado da análise
            
        Raises:
            RuntimeError: Se erro na execução da análise
        """
        pass


class IParameterValidator(ABC):
    """Interface para validação de parâmetros."""
    
    @abstractmethod
    def validar_parametros(self, tipo_analise: str, repositorio_nome: Optional[str], 
                          codigo_entrada: Optional[Union[str, Dict[str, str]]]) -> bool:
        """Valida parâmetros de entrada.
        
        Args:
            tipo_analise: Tipo de análise
            repositorio_nome: Nome do repositório (opcional)
            codigo_entrada: Código de entrada (opcional)
            
        Returns:
            True se válidos
            
        Raises:
            ValueError: Se parâmetros inválidos
        """
        pass


class ICodeProcessor(ABC):
    """Interface para processamento de código."""
    
    @abstractmethod
    def preparar_codigo(self, tipo_analise: str, repositorio_nome: Optional[str], 
                       codigo_entrada: Optional[Union[str, Dict[str, str]]]) -> Union[str, Dict[str, str]]:
        """Prepara código para análise.
        
        Args:
            tipo_analise: Tipo de análise
            repositorio_nome: Nome do repositório
            codigo_entrada: Código de entrada
            
        Returns:
            Código preparado para análise
        """
        pass
    
    @abstractmethod
    def montar_codigo_para_llm(self, codigo_entrada: Union[str, Dict[str, str]]) -> str:
        """Monta código em formato adequado para LLM.
        
        Args:
            codigo_entrada: Código de entrada
            
        Returns:
            Código formatado para LLM
        """
        pass