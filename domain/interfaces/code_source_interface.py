from typing import Dict

class ICodeSource:
    def obter_codigo(self, repositorio: str, tipo_analise: str) -> Dict[str, str]:
        raise NotImplementedError