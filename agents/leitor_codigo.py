from agents.contexto import AnaliseContexto
from tools import github_reader

class LeitorCodigo:
    """
    Responsável por obter o código a ser analisado, seja de um repositório ou diretamente.
    """
    def obter_codigo(self, contexto: AnaliseContexto):
        if contexto.codigo is not None:
            return contexto.codigo
        return github_reader.main(repo=contexto.repositorio, tipo_de_analise=contexto.tipo_analise)
