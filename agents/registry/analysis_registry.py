from typing import Set, Dict, Any


class AnalysisRegistry:
    """Registry extensível para tipos de análise."""
    
    def __init__(self):
        """Inicializa o registry com tipos padrão."""
        self._registered_types: Set[str] = set()
        self._analysis_configs: Dict[str, Dict[str, Any]] = {}
        
        # Registra tipos padrão
        self._register_default_types()
    
    def _register_default_types(self) -> None:
        """Registra os tipos de análise padrão do sistema."""
        default_types = ["design", "pentest", "seguranca", "terraform"]
        for analysis_type in default_types:
            self.register_analysis_type(analysis_type)
    
    def register_analysis_type(
        self, 
        analysis_type: str, 
        config: Dict[str, Any] = None
    ) -> None:
        """Registra um novo tipo de análise.
        
        Args:
            analysis_type: Nome do tipo de análise
            config: Configurações específicas do tipo (opcional)
        """
        self._registered_types.add(analysis_type)
        if config:
            self._analysis_configs[analysis_type] = config
    
    def unregister_analysis_type(self, analysis_type: str) -> None:
        """Remove um tipo de análise do registry.
        
        Args:
            analysis_type: Nome do tipo de análise a remover
        """
        self._registered_types.discard(analysis_type)
        self._analysis_configs.pop(analysis_type, None)
    
    def get_registered_types(self) -> Set[str]:
        """Retorna todos os tipos de análise registrados.
        
        Returns:
            Conjunto de tipos de análise registrados
        """
        return self._registered_types.copy()
    
    def is_registered(self, analysis_type: str) -> bool:
        """Verifica se um tipo de análise está registrado.
        
        Args:
            analysis_type: Nome do tipo de análise
            
        Returns:
            True se o tipo estiver registrado, False caso contrário
        """
        return analysis_type in self._registered_types
    
    def get_analysis_config(self, analysis_type: str) -> Dict[str, Any]:
        """Retorna a configuração de um tipo de análise.
        
        Args:
            analysis_type: Nome do tipo de análise
            
        Returns:
            Configuração do tipo de análise
        """
        return self._analysis_configs.get(analysis_type, {})


# Instância global do registry
analysis_registry = AnalysisRegistry()
