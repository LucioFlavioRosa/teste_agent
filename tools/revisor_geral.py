import os
import time
from typing import Dict
from openai import OpenAI

# Suporte opcional ao Google Colab userdata (fallback para variáveis de ambiente)
try:
    from google.colab import userdata as colab_user_data  # type: ignore
except Exception:  # pragma: no cover
    colab_user_data = None  # type: ignore


def _get_secret(nome: str):
    if colab_user_data is not None:
        try:
            val = colab_user_data.get(nome)
            if val:
                return val
        except Exception:
            pass
    return os.getenv(nome)


OPENAI_API_KEY = _get_secret('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")

openai_client = OpenAI(api_key=OPENAI_API_KEY)


def carregar_prompt(tipo_analise: str) -> str:
    """Carrega o conteúdo do arquivo de prompt correspondente. Fornece fallback padrão se não encontrado."""
    caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"AVISO: Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}. Usando prompt padrão.")
        return (
            "Você é um analista sênior. Analise o código a seguir de forma estruturada, "
            "considerando o tipo de análise solicitado. Aponte riscos, melhorias e recomendações acionáveis."
        )


def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int
) -> str:

    prompt_sistema = carregar_prompt(tipo_analise)

    mensagens = [
        {"role": "system", "content": prompt_sistema},
        {"role": "user", "content": codigo},
        {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
    ]

    timeout_seconds = int(os.getenv('OPENAI_TIMEOUT_SECONDS', '60'))
    max_retries = int(os.getenv('OPENAI_MAX_RETRIES', '3'))

    last_err: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            print(f"INFO: Chamando OpenAI. Analise='{tipo_analise}', modelo='{model_name}', tentativa={attempt}/{max_retries}, input_len={len(codigo)}")
            response = openai_client.chat.completions.create(
                model=model_name,
                messages=mensagens,
                temperature=0.5,
                max_tokens=max_token_out,
                timeout=timeout_seconds
            )
            conteudo_resposta = response.choices[0].message.content.strip()
            return conteudo_resposta
        except Exception as e:
            last_err = e
            if attempt >= max_retries:
                print(f"ERRO: Falha na chamada à API da OpenAI para análise '{tipo_analise}' após {attempt} tentativas. Causa: {e}")
                raise RuntimeError(
                    f"Erro ao comunicar com a OpenAI (analise='{tipo_analise}', modelo='{model_name}', input_len={len(codigo)}): {e}"
                ) from e
            backoff = min(2 ** (attempt - 1), 8)
            print(f"AVISO: Tentativa {attempt} falhou (analise='{tipo_analise}'). Retentando em {backoff}s...")
            time.sleep(backoff)

    # fallback impossível de alcançar se raise acima for executado
    raise RuntimeError(f"Falha desconhecida ao comunicar com a OpenAI: {last_err}")
