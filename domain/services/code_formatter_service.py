class CodeFormatterService:
    @staticmethod
    def montar_codigo_para_llm(codigo_entrada):
        if isinstance(codigo_entrada, dict):
            return '\n\n'.join(f"# Arquivo: {k}\n{v}" for k, v in codigo_entrada.items())
        return str(codigo_entrada)