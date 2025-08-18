from typing import Optional, Dict, Any, Tuple, List, Union
import os
from tools import github_reader
from tools.revisor_geral import executar_analise_llm

# Configurações por ambiente com padrões sensatos
MODEL_NAME_DEFAULT = os.getenv('MODEL_NAME', 'gpt-4.1')
MAX_TOKENS_OUT_DEFAULT = int(os.getenv('MAX_TOKENS_OUT', '3000'))
MAX_INPUT_CHARS_DEFAULT = int(os.getenv('MAX_INPUT_CHARS', '200000'))
PER_FILE_LIMIT_CHARS_DEFAULT = int(os.getenv('PER_FILE_LIMIT_CHARS', '50000'))

analises_validas = ["design", "pentest", "seguranca", "terraform"]

DEFAULT_TEXT_EXTS = [
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".tf", ".tfvars",
    ".json", ".yaml", ".yml",
    ".md", ".markdown",
    ".sh"
]

PRIORIDADE_EXT_POR_ANALISE: Dict[str, List[str]] = {
    "terraform": [".tf", ".tfvars", ".yaml", ".yml", ".json", "Dockerfile", ".py", ".md"] + [".sh"],
    "seguranca": DEFAULT_TEXT_EXTS + ["Dockerfile"],
    "pentest": DEFAULT_TEXT_EXTS + ["Dockerfile"],
    "design": DEFAULT_TEXT_EXTS + ["Dockerfile"]
}


def code_from_repo(repositorio: str, tipo_analise: str) -> Dict[str, str]:
    try:
        print('Iniciando a leitura do repositório: ' + repositorio)
        codigo_para_analise = github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo_para_analise
    except Exception as e:
        raise RuntimeError(f"Falha ao ler o repositório '{repositorio}' para análise '{tipo_analise}': {e}") from e


def validation(tipo_analise: str,
               repositorio: Optional[str] = None,
               codigo: Optional[Union[str, Dict[str, str]]] = None) -> Union[str, Dict[str, str]]:

    if tipo_analise not in analises_validas:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {analises_validas}")

    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")

    if codigo is None:
        codigo_para_analise = code_from_repo(tipo_analise=tipo_analise, repositorio=repositorio)  # dict
    else:
        if isinstance(codigo, (str, dict)):
            codigo_para_analise = codigo
        else:
            raise ValueError("O parâmetro 'codigo' deve ser string ou dicionário {caminho: conteudo}.")

    return codigo_para_analise


def _obter_extensao(caminho: str) -> str:
    base = os.path.basename(caminho)
    if base == 'Dockerfile':
        return 'Dockerfile'
    return os.path.splitext(caminho)[1].lower()


def _ordenar_arquivos_por_prioridade(tipo_analise: str,
                                     arquivos: Dict[str, str]) -> List[Tuple[str, str]]:
    prioridade = PRIORIDADE_EXT_POR_ANALISE.get(tipo_analise, DEFAULT_TEXT_EXTS)
    rank: Dict[str, int] = {ext: i for i, ext in enumerate(prioridade)}

    itens = [(p, c) for p, c in arquivos.items() if not p.startswith('__')]

    def chave(item: Tuple[str, str]) -> Tuple[int, int, str]:
        caminho, conteudo = item
        ext = _obter_extensao(caminho)
        r = rank.get(ext, 10_000)
        return (r, len(conteudo or ''), caminho)

    return sorted(itens, key=chave)


def _formatar_entrada_llm(tipo_analise: str,
                           codigo: Union[str, Dict[str, str]],
                           max_input_chars: int,
                           per_file_limit_chars: int) -> Tuple[str, Dict[str, Any]]:
    telemetria: Dict[str, Any] = {
        'arquivos_total': 0,
        'arquivos_incluidos': 0,
        'arquivos_truncados': 0,
        'caracteres_entrada_original': 0,
        'caracteres_enviados': 0,
        'limite_atingido': False
    }

    if isinstance(codigo, str):
        original_len = len(codigo)
        telemetria['arquivos_total'] = 1
        telemetria['caracteres_entrada_original'] = original_len
        conteudo = codigo[:max_input_chars]
        if original_len > max_input_chars:
            telemetria['arquivos_truncados'] = 1
            telemetria['limite_atingido'] = True
        resultado = f"===== INPUT =====\n{conteudo}\n"
        telemetria['arquivos_incluidos'] = 1
        telemetria['caracteres_enviados'] = len(resultado)
        return resultado, telemetria

    # Se for dicionário {caminho: conteudo}
    arquivos = {k: v for k, v in codigo.items() if not k.startswith('__')}
    telemetria['arquivos_total'] = len(arquivos)
    telemetria['caracteres_entrada_original'] = sum(len(v or '') for v in arquivos.values())

    linhas: List[str] = []
    enviados = 0

    for caminho, conteudo in _ordenar_arquivos_por_prioridade(tipo_analise, arquivos):
        texto = conteudo or ''
        if len(texto) > per_file_limit_chars:
            texto = texto[:per_file_limit_chars]
            telemetria['arquivos_truncados'] += 1
        bloco = f"===== {caminho} =====\n{texto}\n"
        if enviados + len(bloco) > max_input_chars:
            restante = max_input_chars - enviados
            if restante <= 0:
                telemetria['limite_atingido'] = True
                break
            # Tenta incluir parte do bloco atual
            header = f"===== {caminho} =====\n"
            cab_len = len(header)
            if cab_len < restante:
                conteudo_restante = texto[:(restante - cab_len)]
                linhas.append(header + conteudo_restante)
                enviados = max_input_chars
                telemetria['arquivos_incluidos'] += 1
                telemetria['arquivos_truncados'] += 1
                telemetria['limite_atingido'] = True
            else:
                telemetria['limite_atingido'] = True
            break
        linhas.append(bloco)
        enviados += len(bloco)
        telemetria['arquivos_incluidos'] += 1

    resultado = ''.join(linhas)
    telemetria['caracteres_enviados'] = len(resultado)
    return resultado, telemetria


def main(tipo_analise: str,
         repositorio: Optional[str] = None,
         codigo: Optional[Union[str, Dict[str, str]]] = None,
         instrucoes_extras: str = "",
         model_name: str = MODEL_NAME_DEFAULT,
         max_token_out: int = MAX_TOKENS_OUT_DEFAULT) -> Dict[str, Any]:

    codigo_para_analise = validation(tipo_analise=tipo_analise, repositorio=repositorio, codigo=codigo)

    if not codigo_para_analise:
        return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}

    max_input_chars = MAX_INPUT_CHARS_DEFAULT
    per_file_limit_chars = PER_FILE_LIMIT_CHARS_DEFAULT

    entrada_formatada, telemetria = _formatar_entrada_llm(
        tipo_analise=tipo_analise,
        codigo=codigo_para_analise,
        max_input_chars=max_input_chars,
        per_file_limit_chars=per_file_limit_chars
    )

    try:
        resultado = executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=str(entrada_formatada),
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
    except Exception as e:
        raise RuntimeError(
            f"Falha ao executar análise '{tipo_analise}' com modelo '{model_name}'. "
            f"Arquivos incluídos: {telemetria.get('arquivos_incluidos')}/{telemetria.get('arquivos_total')}, "
            f"caracteres enviados: {telemetria.get('caracteres_enviados')}. Causa: {e}"
        ) from e

    return {
        "tipo_analise": tipo_analise,
        "resultado": resultado,
        "telemetria": telemetria,
        "modelo": model_name,
        "max_token_out": max_token_out
    }


def executar_analise(tipo_analise: str,
                     repositorio: Optional[str] = None,
                     codigo: Optional[Union[str, Dict[str, str]]] = None,
                     instrucoes_extras: str = "",
                     model_name: str = MODEL_NAME_DEFAULT,
                     max_token_out: int = MAX_TOKENS_OUT_DEFAULT) -> Dict[str, Any]:
    """Função de compatibilidade que delega para main."""
    return main(
        tipo_analise=tipo_analise,
        repositorio=repositorio,
        codigo=codigo,
        instrucoes_extras=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )
