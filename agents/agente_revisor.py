from typing import Optional, Dict, Any, Callable
from tools import github_reader
from tools.revisor_geral import executar_analise_llm


# Factory para tipos de análise
class AnaliseFactory:
    _analises_registradas = {
        'design': 'python',
        'pentest': 'python',
        'seguranca': 'python',
        'terraform': 'terraform'
    }

    @classmethod
    def tipos_validos(cls):
        return list(cls._analises_registradas.keys())

    @classmethod
    def get_extensao_para_analise(cls, tipo_analise: str):
        return cls._analises_registradas.get(tipo_analise)

    @classmethod
    def registrar_analise(cls, tipo: str, extensao: str):
        cls._analises_registradas[tipo] = extensao


def obter_codigo_para_analise(repositorio: str, tipo_analise: str) -> Dict[str, str]:
    """Adapter para leitura de código de diferentes fontes."""
    print(f'Iniciando a leitura do repositório: {repositorio}')
    return github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)


def validar_parametros(tipo_analise: str, repositorio: Optional[str], codigo: Optional[str]):
    tipos_validos = AnaliseFactory.tipos_validos()
    if tipo_analise not in tipos_validos:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {tipos_validos}")
    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")


def preparar_codigo_para_analise(tipo_analise: str, repositorio: Optional[str], codigo: Optional[str]) -> Dict[str, str]:
    if codigo is not None:
        return codigo
    return obter_codigo_para_analise(repositorio, tipo_analise)


def executar_analise(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[str] = None,
    instrucoes_extras: str = "",
    model_name: str = 'gpt-4.1',
    max_token_out: int = 3000
) -> Dict[str, Any]:
    """
    Orquestrador principal da análise. Separa validação, preparação de código e execução.
    """
    validar_parametros(tipo_analise, repositorio, codigo)
    codigo_para_analise = preparar_codigo_para_analise(tipo_analise, repositorio, codigo)
    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
    resultado = executar_analise_llm(
        tipo_analise=tipo_analise,
        codigo=str(codigo_para_analise),
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}
