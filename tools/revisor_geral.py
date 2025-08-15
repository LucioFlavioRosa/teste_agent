import os
from openai import OpenAI
from typing import Dict


def carregar_prompt(tipo_analise: str) -> str:
    """Carrega o conteúdo do arquivo de prompt correspondente."""
    caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")


def _obter_cliente_openai() -> OpenAI:
    """Inicializa o cliente OpenAI de forma tardia (lazy) e segura."""
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("Variável de ambiente OPENAI_API_KEY não encontrada. Configure a chave da API.")
    return OpenAI(api_key=api_key)


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
        {"role": "user", "content": f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
    ]

    try:
        openai_client = _obter_cliente_openai()
        response = openai_client.chat.completions.create(
            model=model_name,
            messages=mensagens,
            temperature=0.5,
            max_tokens=max_token_out
        )
        conteudo_resposta = response.choices[0].message.content.strip()
        return conteudo_resposta

    except Exception:
        # Padroniza a mensagem de erro sem expor detalhes sensíveis
        raise RuntimeError("Erro ao comunicar com o provedor de IA.")
