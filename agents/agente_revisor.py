from typing import Optional, Dict, Any
from tools.github_reader import GithubRepoReader
from tools.revisor_geral import executar_analise_llm


class AnaliseRegistry:
    """Registry para tipos de análise."""
    _analises = {}

    @classmethod
    def register(cls, nome: str, handler):
        cls._analises[nome] = handler

    @classmethod
    def get(cls, nome: str):
        return cls._analises.get(nome)

    @classmethod
    def valid_types(cls):
        return list(cls._analises.keys())


def obter_codigo(repositorio: str, tipo_analise: str):
    """Obtém o código do repositório para análise."""
    try:
        print(f'Iniciando a leitura do repositório: {repositorio}')
        reader = GithubRepoReader()
        return reader.ler_codigo(repo=repositorio, tipo_de_analise=tipo_analise)
    except Exception as e:
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e


def validar_entrada(tipo_analise: str,
                    repositorio: Optional[str] = None,
                    codigo: Optional[str] = None):
    tipos_validos = AnaliseRegistry.valid_types()
    if tipo_analise not in tipos_validos:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {tipos_validos}")
    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")
    if codigo is None:
        return obter_codigo(repositorio, tipo_analise)
    return codigo


def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo: Optional[str] = None,
                     instrucoes_extras: str = "",
                     model_name: str = 'gpt-4.1',
                     max_token_out: int = 3000) -> Dict[str, Any]:
    codigo_para_analise = validar_entrada(tipo_analise=tipo_analise,
                                          repositorio=repositorio,
                                          codigo=codigo)
    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
    handler = AnaliseRegistry.get(tipo_analise)
    if handler is None:
        return {"tipo_analise": tipo_analise, "resultado": f'Tipo de análise não suportado: {tipo_analise}'}
    resultado = handler(
        tipo_analise=tipo_analise,
        codigo=str(codigo_para_analise),
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}


def _registrar_analises_padrao():
    AnaliseRegistry.register('design', executar_analise_llm)
    AnaliseRegistry.register('pentest', executar_analise_llm)
    AnaliseRegistry.register('seguranca', executar_analise_llm)
    AnaliseRegistry.register('terraform', executar_analise_llm)

_registrar_analises_padrao()
