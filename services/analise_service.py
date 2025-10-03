# -*- coding: utf-8 -*-
"""analise_service.py

Camada de serviço para abstração da lógica de análise.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from agents import agente_revisor


class IAnaliseService(ABC):
    """Interface para serviços de análise."""
    
    @abstractmethod
    def executar_analise(
        self, 
        tipo_analise: str, 
        repositorio: Optional[str] = None, 
        codigo: Optional[str] = None, 
        instrucoes_extras: str = ''
    ) -> Dict[str, Any]:
        """Executa uma análise baseada nos parâmetros fornecidos.
        
        Args:
            tipo_analise: Tipo da análise a ser executada
            repositorio: URL ou nome do repositório (opcional)
            codigo: Código fonte para análise (opcional)
            instrucoes_extras: Instruções adicionais para a análise
            
        Returns:
            Dict contendo o resultado da análise
            
        Raises:
            Exception: Em caso de erro durante a análise
        """
        pass


class AnaliseService(IAnaliseService):
    """Implementação concreta do serviço de análise."""
    
    def __init__(self):
        """Inicializa o serviço de análise."""
        pass
    
    def executar_analise(
        self, 
        tipo_analise: str, 
        repositorio: Optional[str] = None, 
        codigo: Optional[str] = None, 
        instrucoes_extras: str = ''
    ) -> Dict[str, Any]:
        """Executa uma análise utilizando o agente revisor.
        
        Args:
            tipo_analise: Tipo da análise a ser executada
            repositorio: URL ou nome do repositório (opcional)
            codigo: Código fonte para análise (opcional)
            instrucoes_extras: Instruções adicionais para a análise
            
        Returns:
            Dict contendo o resultado da análise
            
        Raises:
            Exception: Em caso de erro durante a análise
        """
        try:
            resultado = agente_revisor.executar_analise(
                tipo_analise=tipo_analise,
                repositorio=repositorio,
                codigo=codigo,
                instrucoes_extras=instrucoes_extras
            )
            return resultado
        except Exception as e:
            raise Exception(f"Falha na execução da análise: {str(e)}")