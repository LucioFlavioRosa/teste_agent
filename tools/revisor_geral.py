import os
import logging
from openai import OpenAI

try:
    from google.colab import userdata as colab_userdata  # fallback opcional
except Exception:  # noqa: BLE001 - ambiente fora do Colab
    colab_userdata = None


logger = logging.getLogger(__name__)

# Cliente OpenAI inicializado sob demanda (lazy)
_openai_client = None


def carregar_prompt(tipo_analise: str) -> str:
    """Carrega o conteúdo do arquivo de prompt correspondente."""
    caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")


def _get_openai_api_key() -> str:
    """Obtém a chave da OpenAI via variável de ambiente com fallback opcional ao Colab."""
    key = os.getenv('OPENAI_API_KEY')
    if not key and colab_userdata:
        try:
            key = colab_userdata.get('OPENAI_API_KEY')
            if key:
                logger.debug("OPENAI_API_KEY obtida via google.colab.userdata.")
        except Exception:  # noqa: BLE001
            key = None
    return key


def get_openai_client() -> OpenAI:
    """Retorna uma instância do cliente OpenAI, inicializando-a sob demanda."""
    global _openai_client
    if _openai_client is None:
        api_key = _get_openai_api_key()
        if not api_key:
            raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client


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
        {'role': 'user', 'content': codigo},
        {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
    ]

    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=model_name,
            messages=mensagens,
            temperature=0.5,
            max_tokens=max_token_out
        )
        conteudo_resposta = response.choices[0].message.content.strip()
        return conteudo_resposta
        
    except Exception as e:  # noqa: BLE001
        logger.exception("Falha na chamada à API da OpenAI para análise '%s'.", tipo_analise)
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {e}") from e
