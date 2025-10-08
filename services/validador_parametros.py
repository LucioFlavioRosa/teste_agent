from typing import Optional, Dict, Any, Union
from services.registro_tipos_analise import RegistroTiposAnalise
import logging

class ValidadorParametros:
    def __init__(self):
        self.registro_tipos = RegistroTiposAnalise()
    
    def validar_parametros_entrada(self, 
                                  tipo_analise: str, 
                                  repositorio_nome: Optional[str] = None, 
                                  codigo_entrada: Optional[Union[str, Dict[str, str]]] = None):
        """Valida os parâmetros de entrada para análise"""
        if not self.registro_tipos.tipo_analise_valido(tipo_analise):
            tipos_validos = self.registro_tipos.obter_tipos_validos()
            raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {tipos_validos}")
        
        if repositorio_nome is None and codigo_entrada is None:
            raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo_entrada'.")
        
        return True