from typing import Optional, Dict, Any, Tuple
from tools import github_reader
from tools.revisor_geral import executar_analise_llm, estimate_tokens, get_model_context_limit


modelo_llm = 'gpt-4.1'
max_tokens_saida = 3000

analises_validas = ["design", "pentest", "seguranca", "terraform"]

# Cache simples do payload montado por repo/ref/tipo/modelo
_PAYLOAD_CACHE: Dict[Tuple[str, str, str, str, int], str] = {}


def code_from_repo(repositorio: str,
                   tipo_analise: str,
                   ref: Optional[str] = None):

    try:
        print('Iniciando a leitura do repositório: ' + repositorio)
        codigo_para_analise = github_reader.main(repo=repositorio,
                                                 tipo_de_analise=tipo_analise,
                                                 ref=ref)
        return codigo_para_analise

    except Exception as e:
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e


def validation(tipo_analise: str,
               repositorio: Optional[str] = None,
               codigo: Optional[Any] = None,
               ref: Optional[str] = None):

    if tipo_analise not in analises_validas:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {analises_validas}")

    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")

    if codigo is None:
        codigo_para_analise = code_from_repo(tipo_analise=tipo_analise,
                                             repositorio=repositorio,
                                             ref=ref)

    else:
        codigo_para_analise = codigo

    return codigo_para_analise


def _montar_payload_textual(arquivos: Dict[str, str],
                            model_name: str,
                            max_token_out: int,
                            instrucoes_extras: str = "") -> str:
    """
    Monta um payload textual delimitado por arquivo, respeitando um orçamento aproximado de tokens
    com base no contexto do modelo e nos tokens reservados para saída.
    """
    context_limit = get_model_context_limit(model_name)
    # Reserva tokens para saída + overhead de mensagens/sistema
    margem_overhead = 1500
    orcamento_codigos = max(0, context_limit - max_token_out - margem_overhead)

    total_tokens = 0
    partes = []

    # Ordena por caminho para previsibilidade, ignora metadados
    for caminho in sorted(k for k in arquivos.keys() if not k.startswith('__')):
        conteudo = arquivos[caminho]
        bloco = f"=== {caminho} ===\n{conteudo}\n"
        custo = estimate_tokens(bloco)
        if total_tokens + custo > orcamento_codigos:
            break
        partes.append(bloco)
        total_tokens += custo

    payload = "".join(partes)

    # Inclui cabeçalho com instruções extras, apenas informativo (não muito longo)
    if instrucoes_extras and instrucoes_extras.strip():
        header = f"\n=== INSTRUCOES_EXTRAS ===\n{instrucoes_extras.strip()}\n\n"
        # Checa se cabe
        if total_tokens + estimate_tokens(header) <= orcamento_codigos + margem_overhead:
            payload = header + payload

    return payload


def main(tipo_analise: str,
         repositorio: Optional[str] = None,
         codigo: Optional[Any] = None,
         instrucoes_extras: str = "",
         model_name: str = modelo_llm,
         max_token_out: int = max_tokens_saida,
         ref: Optional[str] = None) -> Dict[str, Any]:

    codigo_para_analise = validation(tipo_analise=tipo_analise,
                                     repositorio=repositorio,
                                     codigo=codigo,
                                     ref=ref)

    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}

    # Se o usuário forneceu texto direto, usa-o. Se for dict de arquivos, monta payload controlado.
    if isinstance(codigo_para_analise, dict):
        meta = codigo_para_analise.get('__meta__', {})
        repo_name = meta.get('repo', str(repositorio or 'desconhecido'))
        ref_sha = meta.get('ref_sha', str(ref or 'HEAD'))
        cache_key = (repo_name, ref_sha, tipo_analise, model_name, int(max_token_out))
        if cache_key in _PAYLOAD_CACHE:
            payload = _PAYLOAD_CACHE[cache_key]
        else:
            payload = _montar_payload_textual(codigo_para_analise, model_name, max_token_out, instrucoes_extras)
            _PAYLOAD_CACHE[cache_key] = payload
    else:
        payload = str(codigo_para_analise)

    resultado = executar_analise_llm(
        tipo_analise=tipo_analise,
        codigo=payload,
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )

    return {"tipo_analise": tipo_analise, "resultado": resultado}


# Compatibilidade com chamadas existentes
executar_analise = main
