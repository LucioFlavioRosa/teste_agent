from agents.contexto import AnaliseContexto

class ValidadorDeParametros:
    """
    Responsável pela validação dos parâmetros de entrada, seguindo SRP.
    """
    ANALISES_VALIDAS = {"design", "pentest", "seguranca", "terraform"}

    def validar(self, contexto: AnaliseContexto):
        if contexto.tipo_analise not in self.ANALISES_VALIDAS:
            raise ValueError(
                f"Tipo de análise '{contexto.tipo_analise}' é inválido. Válidos: {self.ANALISES_VALIDAS}")
        if contexto.repositorio is None and contexto.codigo is None:
            raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")
