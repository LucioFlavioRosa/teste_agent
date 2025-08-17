from typing import Optional, Dict, Any
from tools import github_reader


modelo_llm = 'gpt-4.1'
max_tokens_saida = 3000

# Tipos de análise válidos explicitamente alinhados ao leitor do GitHub
analises_validas = list(github_reader.MAPEAMENTO_TIPO_EXTENSOES.keys())


def code_from_repo(repositorio: str,
                   tipo_analise: str):

    try:
        print('Iniciando a leitura do repositório: ' + repositorio)
        codigo_para_analise = github_reader.main(repo=repositorio,
                                                 tipo_de_analise=tipo_analise)

        return codigo_para_analise

    except Exception as e:
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e


def validation(tipo_analise: str,
               repositorio: Optional[str] = None,
               codigo: Optional[str] = None):

    if tipo_analise not in analises_validas:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {analises_validas}")

    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")

    if codigo is None:
        codigo_para_analise = code_from_repo(tipo_analise=tipo_analise,
                                             repositorio=repositorio)

    else:
        codigo_para_analise = codigo

    return codigo_para_analise


def main(tipo_analise: str,
         repositorio: Optional[str] = None,
         codigo: Optional[str] = None,
         instrucoes_extras: str = "",
         model_name: str = modelo_llm,
         max_token_out: int = max_tokens_saida) -> Dict[str, Any]:

    # Import tardio para evitar efeitos colaterais em import do módulo
    from tools.revisor_geral import executar_analise_llm

    codigo_para_analise = validation(tipo_analise=tipo_analise,
                                     repositorio=repositorio,
                                     codigo=codigo)

    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}

    else:
        resultado = executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=str(codigo_para_analise),
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )

        return {"tipo_analise": tipo_analise, "resultado": resultado}


def executar_analise(*args, **kwargs) -> Dict[str, Any]:
    """Alias público para compatibilidade com chamadas externas."""
    return main(*args, **kwargs)
