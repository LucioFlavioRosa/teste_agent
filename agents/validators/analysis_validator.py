from typing import Optional, Set


class AnalysisValidator:
    """Responsável pela validação de parâmetros de análise."""
    
    def __init__(self, valid_analysis_types: Set[str]):
        """Inicializa o validador com tipos de análise válidos.
        
        Args:
            valid_analysis_types: Conjunto de tipos de análise válidos
        """
        self._valid_analysis_types = valid_analysis_types
    
    def validate_analysis_type(self, tipo_analise: str) -> None:
        """Valida se o tipo de análise é válido.
        
        Args:
            tipo_analise: Tipo de análise a validar
            
        Raises:
            ValueError: Se o tipo de análise for inválido
        """
        if tipo_analise not in self._valid_analysis_types:
            raise ValueError(
                f"Tipo de análise '{tipo_analise}' é inválido. "
                f"Válidos: {list(self._valid_analysis_types)}"
            )
    
    def validate_input_sources(
        self, 
        repositorio: Optional[str], 
        codigo: Optional[str]
    ) -> None:
        """Valida se pelo menos uma fonte de código foi fornecida.
        
        Args:
            repositorio: Nome do repositório (opcional)
            codigo: Código direto (opcional)
            
        Raises:
            ValueError: Se nenhuma fonte de código for fornecida
        """
        if repositorio is None and codigo is None:
            raise ValueError(
                "Erro: É obrigatório fornecer 'repositorio' ou 'codigo'."
            )
    
    def get_valid_analysis_types(self) -> Set[str]:
        """Retorna os tipos de análise válidos.
        
        Returns:
            Conjunto de tipos de análise válidos
        """
        return self._valid_analysis_types.copy()
