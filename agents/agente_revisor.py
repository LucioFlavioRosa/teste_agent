from typing import Optional, Dict, Any
import logging
from tools import github_reader
from tools.revisor_geral import executar_analise_llm 

modelo_llm = 'gpt-4.1'
max_tokens_saida = 3000

analises_validas = ["design", "pentest", "seguranca", "terraform"]

def executar_analise(*args, **kwargs):
    """Wrapper para manter contrato com chamadores externos."""
    return main(*args, **kwargs)

def validar_entrada(tipo_analise: str, repositorio: Optional[str], codigo: Optional[str]):
    if tipo_analise not in analises_validas:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {analises_validas}")
    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")

def obter_codigo(tipo_analise: str, repositorio: Optional[str], codigo: Optional[str]):
    if codigo is not None:
        return codigo
    else:
        return code_from_repo(repositorio=repositorio, tipo_analise=tipo_analise)

def preparar_codigo_para_analise(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None):
    validar_entrada(tipo_analise, repositorio, codigo)
    return obter_codigo(tipo_analise, repositorio, codigo)

def code_from_repo(repositorio: str, tipo_analise: str):
    try:
        logging.info(f'Iniciando a leitura do repositório: {repositorio}')
        codigo_para_analise = github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo_para_analise
    except Exception as e:
        logging.error(f"Falha ao executar a análise de '{tipo_analise}': {e}")
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e

def montar_payload_para_llm(arquivos: Dict[str, str]) -> str:
    """Gera string estruturada para análise LLM, separando arquivos."""
    if not arquivos:
        return ""
    partes = []
    for path, conteudo in arquivos.items():
        partes.append(f"--- {path} ---\n{conteudo}")
    return '\n\n'.join(partes)

def main(tipo_analise: str,
         repositorio: Optional[str] = None,
         codigo: Optional[str] = None,
         instrucoes_extras: str = "",
         model_name: str = modelo_llm,
         max_token_out: int = max_tokens_saida) -> Dict[str, Any]:

    codigo_para_analise = preparar_codigo_para_analise(tipo_analise=tipo_analise,
                                                       repositorio=repositorio,
                                                       codigo=codigo)
    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Nenhum arquivo elegível encontrado para análise.'}
    # Se for dict (de arquivos), montar payload estruturado
    if isinstance(codigo_para_analise, dict):
        payload = montar_payload_para_llm(codigo_para_analise)
    else:
        payload = codigo_para_analise

    resultado = executar_analise_llm(
        tipo_analise=tipo_analise,
        codigo=payload,
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
    return {"tipo_analise": tipo_analise, "resultado": resultado}
