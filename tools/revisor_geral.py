import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def _obter_api_key_openai() -> str:
    """Obtém a API Key da OpenAI de maneira portátil.

    Ordem de busca:
    1) Variável de ambiente OPENAI_API_KEY
    2) google.colab.userdata['OPENAI_API_KEY'] (fallback opcional)
    """
    chave = os.getenv('OPENAI_API_KEY')
    if chave:
        return chave
    # Fallback opcional ao Colab
    try:
        from google.colab import userdata  # type: ignore
        chave = userdata.get('OPENAI_API_KEY')
        if chave:
            return chave
    except Exception:
        pass
    raise ValueError(
        "A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY ou configure via google.colab.userdata['OPENAI_API_KEY']."
    )


OPENAI_API_KEY = _obter_api_key_openai()
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def carregar_prompt(tipo_analise: str) -> str:
    """Carrega o conteúdo do arquivo de prompt correspondente.

    Caso o arquivo não exista, retorna um prompt padrão de fallback.
    """
    caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.warning("Arquivo de prompt para a análise '%s' não encontrado em: %s. Usando fallback padrão.", tipo_analise, caminho_prompt)
        return (
            "Você é um assistente especialista em revisão de código. Analise o conteúdo fornecido, "
            "identifique problemas, riscos e melhorias, e produza recomendações práticas e priorizadas."
        )


def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int,
) -> str:
    """Executa a análise via OpenAI Chat Completions e retorna o texto de saída."""
    prompt_sistema = carregar_prompt(tipo_analise)

    mensagens = [
        {"role": "system", "content": prompt_sistema},
        {"role": "user", "content": codigo},
        {
            "role": "user",
            "content": (
                f"Instruções extras do usuário a serem consideradas na análise: {analise_extra}"
                if analise_extra.strip()
                else "Nenhuma instrução extra fornecida pelo usuário."
            ),
        },
    ]

    try:
        resp = openai_client.chat.completions.create(
            model=model_name,
            messages=mensagens,
            temperature=0.5,
            max_tokens=max_token_out,
        )
        conteudo_resposta = resp.choices[0].message.content.strip()
        return conteudo_resposta
    except Exception as e:
        logger.exception("Falha na chamada à API da OpenAI para análise '%s'", tipo_analise)
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {e}") from e
