class TipoAnalise:
    _registry = set()

    @classmethod
    def registrar(cls, tipo):
        cls._registry.add(tipo)

    @classmethod
    def tipos_validos(cls):
        return list(cls._registry)

    @classmethod
    def validar(cls, tipo):
        if tipo not in cls._registry:
            raise ValueError(f"Tipo de análise '{tipo}' é inválido. Válidos: {cls.tipos_validos()}")
        return True

# Registro padrão
TipoAnalise.registrar("design")
TipoAnalise.registrar("pentest")
TipoAnalise.registrar("seguranca")
TipoAnalise.registrar("terraform")