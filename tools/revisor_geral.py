import os
import time
import random
from typing import Dict, List
from openai import OpenAI
from google.colab import userdata


OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")

# Timeout padrão para chamadas
DEFAULT_TIMEOUT = 60

openai_client = OpenAI(api_key=OPENAI_API_KEY, timeout=DEFAULT_TIMEOUT)


def carregar_prompt(tipo_analise: str) -> str:
    """Carrega o conteúdo do arquivo de prompt correspondente."""
    caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")


def estimate_tokens(text: str) -> int:
    """Estimativa simples: ~4 caracteres por token."""
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)


def get_model_context_limit(model_name: str) -> int:
    model_name = (model_name or '').lower()
    # Heurística de limites; ajustar conforme necessário
    mapping = {
        'gpt-4.1': 128000,
        'gpt-4o': 128000,
        'gpt-4-1106-preview': 128000,
        'gpt-3.5-turbo-16k': 16000,
        'gpt-3.5-turbo': 16000,
    }
    return mapping.get(model_name, 128000)


def _call_with_retries(model: str, messages: List[Dict[str, str]], max_tokens: int, temperature: float = 0.5, timeout: int = DEFAULT_TIMEOUT, retries: int = 3) -> str:
    backoff = 1.5
    delay = 2.0
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            last_err = e
            if attempt >= retries:
                break
            sleep_time = delay * (backoff ** (attempt - 1)) + random.uniform(0, 0.5)
            print(f"WARN: Falha na chamada OpenAI (tentativa {attempt}/{retries}): {e}. Retentando em {sleep_time:.1f}s...")
            time.sleep(sleep_time)
    raise RuntimeError(f"Erro ao comunicar com a OpenAI após {retries} tentativas: {last_err}")


def _chunk_text_by_budget(text: str, target_tokens_per_chunk: int) -> List[str]:
    """Divide o texto em chunks aproximados por orçamento de tokens, tentando respeitar separadores por arquivo."""
    if not text:
        return []

    parts: List[str] = []
    current: List[str] = []
    current_tokens = 0

    # Tenta dividir por arquivos se houver delimitadores
    lines = text.splitlines(keepends=True)
    for line in lines:
        t = estimate_tokens(line)
        if current_tokens + t > target_tokens_per_chunk and current:
            parts.append(''.join(current))
            current = []
            current_tokens = 0
        current.append(line)
        current_tokens += t

    if current:
        parts.append(''.join(current))

    return parts


def _summarize_chunks(tipo_analise: str, model_name: str, prompt_sistema: str, chunks: List[str], analise_extra: str, max_token_out: int) -> List[str]:
    """Produz um sumário por chunk para permitir análise hierárquica."""
    resumos: List[str] = []
    # Reserva tokens de saída por resumo (curto) para manter eficiência
    per_chunk_out = max(512, min(1500, max_token_out))
    for idx, chunk in enumerate(chunks, start=1):
        mensagens = [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": f"Subconjunto {idx} do código (delimitado por arquivos):\n{chunk}"},
        ]
        if analise_extra and analise_extra.strip():
            mensagens.append({"role": "user", "content": f"Instruções extras a considerar neste subconjunto: {analise_extra}"})
        resumo = _call_with_retries(
            model=model_name,
            messages=mensagens,
            max_tokens=per_chunk_out,
            temperature=0.4,
        )
        resumos.append(f"=== RESUMO_CHUNK_{idx} ===\n{resumo}\n")
    return resumos


def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int
) -> str:

    prompt_sistema = carregar_prompt(tipo_analise)

    context_limit = get_model_context_limit(model_name)

    # Monta mensagens base
    mensagens_base = [
        {"role": "system", "content": prompt_sistema},
        {"role": "user", "content": codigo},
    ]
    if analise_extra and analise_extra.strip():
        mensagens_base.append({"role": "user", "content": f"Instruções extras do usuário a serem consideradas na análise: {analise_extra}"})
    else:
        mensagens_base.append({"role": "user", "content": 'Nenhuma instrução extra fornecida pelo usuário.'})

    # Verifica orçamento de contexto aproximado; se exceder, faz sumarização em chunks
    tokens_estimados = sum(estimate_tokens(m.get('content', '')) for m in mensagens_base) + max_token_out

    if tokens_estimados <= context_limit:
        try:
            return _call_with_retries(
                model=model_name,
                messages=mensagens_base,
                max_tokens=max_token_out,
                temperature=0.5,
            )
        except Exception as e:
            print(f"ERRO: Falha na chamada direta à API da OpenAI para análise '{tipo_analise}'. Causa: {e}")
            raise

    # Sumarização hierárquica
    # Seleciona um orçamento de entrada por chunk, reservando espaço para saída e overhead
    margem_overhead = 2000
    orcamento_entrada = max(4096, context_limit - max_token_out - margem_overhead)
    chunks = _chunk_text_by_budget(codigo, target_tokens_per_chunk=orcamento_entrada)
    if not chunks:
        chunks = [codigo]

    try:
        resumos = _summarize_chunks(
            tipo_analise=tipo_analise,
            model_name=model_name,
            prompt_sistema=prompt_sistema,
            chunks=chunks,
            analise_extra=analise_extra,
            max_token_out=max_token_out,
        )

        # Chamada final consolidando os resumos
        consolidado = "\n".join(resumos)
        mensagens_finais = [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": "Abaixo estão resumos parciais da análise por subconjunto de arquivos. Consolide-os em um relatório final coerente, sem redundâncias, apontando riscos, melhorias e recomendações priorizadas."},
            {"role": "user", "content": consolidado},
        ]
        if analise_extra and analise_extra.strip():
            mensagens_finais.append({"role": "user", "content": f"Reforce as seguintes instruções do usuário ao consolidar: {analise_extra}"})

        return _call_with_retries(
            model=model_name,
            messages=mensagens_finais,
            max_tokens=max_token_out,
            temperature=0.5,
        )

    except Exception as e:
        print(f"ERRO: Falha na execução de sumarização hierárquica para '{tipo_analise}'. Causa: {e}")
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {e}") from e
