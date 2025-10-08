from typing import Union, Dict

class MontadorCodigo:
    def montar_codigo_para_llm(self, codigo_entrada: Union[str, Dict[str, str]]) -> str:
        """
        Concatena o conteúdo dos arquivos se o código for um dicionário, 
        ou retorna a string diretamente.
        """
        if isinstance(codigo_entrada, dict):
            return '\n\n'.join(f"# Arquivo: {k}\n{v}" for k, v in codigo_entrada.items())
        return str(codigo_entrada)