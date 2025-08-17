import os
from openai import OpenAI


def carregar_prompt(tipo_analise: str) -> str:
    """Carrega o conteúdo do arquivo de prompt correspondente."""
    caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")


def get_openai_client(api_key: str | None = None) -> OpenAI:
    """Fornece um cliente OpenAI usando API key da env ou parâmetro (para testes)."""
    key = api_key or os.getenv('OPENAI_API_KEY')
    if not key:
        raise ValueError('OPENAI_API_KEY não configurada')
    return OpenAI(api_key=key)


def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int,
    client: OpenAI | None = None
) -> str:
    """Executa a análise usando LLM com inicialização tardia e injeção de cliente opcional."""

    prompt_sistema = carregar_prompt(tipo_analise)

    mensagens = [
        {"role": "system", "content": prompt_sistema},
        {"role": "user", "content": codigo},
        {"role": "user", "content": f"Instruções extras do usuário a serem consideradas na análise: {analise_extra}" if analise_extra.strip() else "Nenhuma instrução extra fornecida pelo usuário."}
    ]

    cli = client or get_openai_client()

    try:
        response = cli.chat.completions.create(
            model=model_name,
            messages=mensagens,
            temperature=0.5,
            max_tokens=max_token_out
        )
        conteudo_resposta = response.choices[0].message.content.strip()
        return conteudo_resposta

    except Exception as e:
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {e}") from e
