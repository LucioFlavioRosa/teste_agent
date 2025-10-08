from typing import List, Dict

class RegistroTiposAnalise:
    def __init__(self):
        self._tipos_registrados = {
            "design": {"extensoes": [".py", ".js", ".java", ".cs"], "descricao": "Análise de design de código"},
            "pentest": {"extensoes": [".py", ".js", ".php", ".rb"], "descricao": "Análise de penetration testing"},
            "seguranca": {"extensoes": [".py", ".js", ".java", ".cs", ".php"], "descricao": "Análise de segurança"},
            "terraform": {"extensoes": [".tf", ".tfvars"], "descricao": "Análise de infraestrutura Terraform"}
        }
    
    def registrar_tipo_analise(self, tipo: str, extensoes: List[str], descricao: str = ""):
        """Registra um novo tipo de análise dinamicamente"""
        self._tipos_registrados[tipo.lower()] = {
            "extensoes": extensoes,
            "descricao": descricao
        }
    
    def tipo_analise_valido(self, tipo: str) -> bool:
        """Verifica se um tipo de análise é válido"""
        return tipo.lower() in self._tipos_registrados
    
    def obter_tipos_validos(self) -> List[str]:
        """Retorna lista de tipos de análise válidos"""
        return list(self._tipos_registrados.keys())
    
    def obter_extensoes_tipo(self, tipo: str) -> List[str]:
        """Retorna as extensões associadas a um tipo de análise"""
        if not self.tipo_analise_valido(tipo):
            raise ValueError(f"Tipo de análise '{tipo}' não registrado")
        return self._tipos_registrados[tipo.lower()]["extensoes"]
    
    def obter_descricao_tipo(self, tipo: str) -> str:
        """Retorna a descrição de um tipo de análise"""
        if not self.tipo_analise_valido(tipo):
            raise ValueError(f"Tipo de análise '{tipo}' não registrado")
        return self._tipos_registrados[tipo.lower()]["descricao"]
    
    def remover_tipo_analise(self, tipo: str):
        """Remove um tipo de análise do registro"""
        if tipo.lower() in self._tipos_registrados:
            del self._tipos_registrados[tipo.lower()]