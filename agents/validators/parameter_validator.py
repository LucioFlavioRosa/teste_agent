from typing import Optional, Dict, Any, Union, List
import logging

class ParameterValidator:
    def __init__(self, tipos_analise_validos: List[str]):
        self.tipos_analise_validos = tipos_analise_validos
    
    def validar_parametros_entrada(self, tipo_analise: str, repositorio_nome: Optional[str] = None, codigo_entrada: Optional[Union[str, Dict[str, str]]] = None):
        if tipo_analise not in self.tipos_analise_validos:
            raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {self.tipos_analise_validos}")
        if repositorio_nome is None and codigo_entrada is None:
            raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo_entrada'.")
        return True