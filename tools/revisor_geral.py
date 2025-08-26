import os
from typing import Dict

def obter_openai_api_key():
    """Obtém a chave da API OpenAI de diferentes fontes."""
    try:
        # Tenta primeiro do Google Colab
        from google.colab import userdata
        return userdata.get('OPENAI_API_KEY')
    except ImportError:
        # Se não estiver no Colab, tenta variável de ambiente
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("A chave da API da OpenAI não foi encontrada. Configure OPENAI_API_KEY como variável de ambiente ou execute no Google Colab.")
        return api_key

def inicializar_cliente_openai():
    """Inicializa o cliente OpenAI com compatibilidade para diferentes versões."""
    OPENAI_API_KEY = obter_openai_api_key()
    if not OPENAI_API_KEY:
        raise ValueError("A chave da API da OpenAI não foi encontrada.")
    
    try:
        # Tenta usar a versão mais recente da biblioteca openai
        from openai import OpenAI
        return OpenAI(api_key=OPENAI_API_KEY), 'v1'
    except ImportError:
        try:
            # Fallback para versão antiga
            import openai
            openai.api_key = OPENAI_API_KEY
            return openai, 'legacy'
        except ImportError:
            raise ImportError("Biblioteca openai não encontrada. Execute: pip install openai")

openai_client, openai_version = inicializar_cliente_openai()

def carregar_prompt(tipo_analise: str) -> str:
    caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError as e:
        raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}") from e

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
        if openai_version == 'v1':
            # Versão nova da biblioteca openai
            response = openai_client.chat.completions.create(
                model=model_name,
                messages=mensagens,
                temperature=0.5,
                max_tokens=max_token_out
            )
            # Validação do formato da resposta
            if hasattr(response, 'choices') and len(response.choices) > 0:
                choice = response.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    conteudo_resposta = choice.message.content.strip()
                    return conteudo_resposta
                else:
                    raise AttributeError("Formato de resposta inesperado: message.content não encontrado")
            else:
                raise AttributeError("Formato de resposta inesperado: choices não encontrado")
        else:
            # Versão legacy da biblioteca openai
            response = openai_client.ChatCompletion.create(
                model=model_name,
                messages=mensagens,
                temperature=0.5,
                max_tokens=max_token_out
            )
            # Validação do formato da resposta para versão legacy
            if 'choices' in response and len(response['choices']) > 0:
                choice = response['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    conteudo_resposta = choice['message']['content'].strip()
                    return conteudo_resposta
                else:
                    raise AttributeError("Formato de resposta inesperado: message.content não encontrado")
            else:
                raise AttributeError("Formato de resposta inesperado: choices não encontrado")
                
    except Exception as e:
        print(f"ERRO: Falha na chamada à API da OpenAI para análise '{tipo_analise}'. Causa: {type(e).__name__}: {e}")
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {type(e).__name__}: {e}") from e