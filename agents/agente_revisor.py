from typing import Optional, Dict, Any
import logging
from tools import github_reader
from tools.revisor_geral import executar_analise_llm

# Configuração básica de logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Modelo compatível com Chat Completions
MODELO_PADRAO = 'gpt-4o'
MAX_TOKENS_SAIDA = 3000

analises_validas = ["design", "pentest", "seguranca", "terraform"]


def codigo_do_repositorio(repositorio: str, tipo_analise: str):
    """Obtém o código de um repositório GitHub para análise.

    Args:
        repositorio: Nome completo do repositório no formato 'owner/repo'.
        tipo_analise: Tipo de análise a ser realizada (usado para filtragem de arquivos).

    Returns:
        Dict[str, str]: Mapeamento caminho_do_arquivo -> conteudo.
    """
    try:
        logger.info("Iniciando a leitura do repositório: %s", repositorio)
        codigo_para_analise = github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo_para_analise
    except Exception as e:
        logger.exception("Falha ao obter código do repositório '%s' para análise '%s'", repositorio, tipo_analise)
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e


def validar_entrada(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None):
    """Valida parâmetros de entrada e resolve a fonte do código a analisar.

    Args:
        tipo_analise: Tipo de análise (deve estar em analises_validas).
        repositorio: Repositório GitHub no formato 'owner/repo'. Opcional se 'codigo' for fornecido.
        codigo: Texto de código cru ou mapeamento de arquivos. Opcional se 'repositorio' for fornecido.

    Returns:
        O código a ser analisado. Pode ser uma string ou um dicionário caminho->conteúdo.
    """
    if tipo_analise not in analises_validas:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {analises_validas}")

    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")

    if codigo is None:
        codigo_para_analise = codigo_do_repositorio(tipo_analise=tipo_analise, repositorio=repositorio)
    else:
        codigo_para_analise = codigo

    return codigo_para_analise


def _formatar_codigo_para_llm(codigo_para_analise: Any) -> str:
    """Formata o código para envio ao LLM.

    - Se for um dicionário de arquivos, concatena com cabeçalhos delimitados por caminho.
    - Caso contrário, converte para string simples.
    """
    if isinstance(codigo_para_analise, dict):
        partes = []
        for caminho in sorted(codigo_para_analise.keys()):
            conteudo = codigo_para_analise[caminho]
            partes.append(f"=== {caminho} ===\n{conteudo}\n")
        return "\n".join(partes)
    return str(codigo_para_analise)


def executar_analise(
    tipo_analise: str,
    repositorio: Optional[str] = None,
    codigo: Optional[str] = None,
    instrucoes_extras: str = "",
    model_name: str = MODELO_PADRAO,
    max_token_out: int = MAX_TOKENS_SAIDA,
) -> Dict[str, Any]:
    """Executa a análise do código utilizando um LLM.

    Returns:
        Dict com chaves: tipo_analise, resultado.
    """
    codigo_para_analise = validar_entrada(tipo_analise=tipo_analise, repositorio=repositorio, codigo=codigo)

    if not codigo_para_analise:
        logger.warning("Nenhum código fornecido para a análise '%s'", tipo_analise)
        return {"tipo_analise": tipo_analise, "resultado": "Não foi fornecido nenhum código para análise"}

    codigo_formatado = _formatar_codigo_para_llm(codigo_para_analise)

    logger.info("Iniciando execução da análise '%s' com modelo '%s'", tipo_analise, model_name)
    resultado = executar_analise_llm(
        tipo_analise=tipo_analise,
        codigo=codigo_formatado,
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out,
    )

    logger.info("Análise '%s' concluída", tipo_analise)
    return {"tipo_analise": tipo_analise, "resultado": resultado}


# Alias para manter compatibilidade retroativa
main = executar_analise  # Interface pública antiga
validation = validar_entrada  # Alias de compatibilidade
code_from_repo = codigo_do_repositorio  # Alias de compatibilidade
modelo_llm = MODELO_PADRAO
max_tokens_saida = MAX_TOKENS_SAIDA
