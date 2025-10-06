import logging
from typing import Dict, Any, Optional


class ValidationErrorHandler:
    """Manipulador específico para erros de validação."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle_validation_error(self, error: ValueError, context: str = "") -> None:
        """Trata erros de validação de parâmetros."""
        error_msg = f"Erro de validação{f' em {context}' if context else ''}: {error}"
        self.logger.error(error_msg)
        raise error


class ExecutionErrorHandler:
    """Manipulador específico para erros de execução."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle_execution_error(self, error: RuntimeError, context: str = "") -> None:
        """Trata erros de execução de operações."""
        error_msg = f"Erro de execução{f' em {context}' if context else ''}: {error}"
        self.logger.error(error_msg)
        raise error


class DataErrorHandler:
    """Manipulador específico para erros de dados (chave, tipo)."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle_key_error(self, error: KeyError, context: str = "") -> None:
        """Trata erros de chave ausente."""
        error_msg = f"Erro de chave{f' em {context}' if context else ''}: {error}"
        self.logger.error(error_msg)
        raise error
    
    def handle_type_error(self, error: TypeError, context: str = "") -> None:
        """Trata erros de tipo de dados."""
        error_msg = f"Erro de tipo{f' em {context}' if context else ''}: {error}"
        self.logger.error(error_msg)
        raise error


class CompositeErrorHandler:
    """Manipulador composto que delega para manipuladores específicos."""
    
    def __init__(self):
        self.validation_handler = ValidationErrorHandler()
        self.execution_handler = ExecutionErrorHandler()
        self.data_handler = DataErrorHandler()
    
    def handle_error(self, error: Exception, context: str = "") -> None:
        """Delega o tratamento do erro para o manipulador apropriado."""
        if isinstance(error, ValueError):
            self.validation_handler.handle_validation_error(error, context)
        elif isinstance(error, RuntimeError):
            self.execution_handler.handle_execution_error(error, context)
        elif isinstance(error, KeyError):
            self.data_handler.handle_key_error(error, context)
        elif isinstance(error, TypeError):
            self.data_handler.handle_type_error(error, context)
        else:
            # Erro genérico
            logger = logging.getLogger(__name__)
            error_msg = f"Erro não categorizado{f' em {context}' if context else ''}: {error}"
            logger.error(error_msg)
            raise error