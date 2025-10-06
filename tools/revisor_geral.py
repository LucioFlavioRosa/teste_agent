import os
from openai import OpenAI
from typing import Dict
from tools.config import config
import logging

# Configura logging usando a configuração centralizada
config.configure_logging()
logger = logging.getLogger(__name__)

# Inicializa cliente OpenAI com configuração flexível
openai_config = config.get_openai_config()
if not openai_config['api_key']:
    raise ValueError("A chave da API da OpenAI não foi encontrada na configuração.")

openai_client = OpenAI(api_key=openai_config['api_key'])

def carregar_prompt(tipo_analise: str) -> str:
    """Carrega prompt de análise do arquivo correspondente."""
    # Permite override do diretório de prompts via variável de ambiente
    prompts_dir = os.getenv('PROMPTS_DIR', os.path.join(os.path.dirname(__file__), 'prompt'))
    caminho_prompt = os.path.join(prompts_dir, f'{tipo_analise}.md')
    
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            content = f.read()
            logger.info(f"Prompt carregado com sucesso para análise '{tipo_analise}'")
            return content
    except FileNotFoundError as e:
        error_msg = f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    except Exception as e:
        error_msg = f"Erro ao carregar prompt para análise '{tipo_analise}': {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str = None,
    max_token_out: int = None
) -> str:
    """Executa análise LLM com configuração flexível."""
    # Usa configurações padrão se não fornecidas
    openai_config = config.get_openai_config()
    if model_name is None:
        model_name = openai_config['model']
    if max_token_out is None:
        max_token_out = openai_config['max_tokens']
    
    try:
        prompt_sistema = carregar_prompt(tipo_analise)
        
        mensagens = [
            {"role": "system", "content": prompt_sistema},
            {'role': 'user', 'content': codigo},
            {
                'role': 'user', 
                'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' 
                          if analise_extra.strip() 
                          else 'Nenhuma instrução extra fornecida pelo usuário.'
            }
        ]
        
        logger.info(f"Executando análise LLM para tipo '{tipo_analise}' com modelo '{model_name}'")
        
        response = openai_client.chat.completions.create(
            model=model_name,
            messages=mensagens,
            temperature=openai_config['temperature'],
            max_tokens=max_token_out
        )
        
        conteudo_resposta = response.choices[0].message.content.strip()
        logger.info(f"Análise LLM concluída com sucesso para tipo '{tipo_analise}'")
        return conteudo_resposta
        
    except Exception as e:
        error_msg = f"Falha na chamada à API da OpenAI para análise '{tipo_analise}'. Causa: {type(e).__name__}: {e}"
        logger.error(error_msg)
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {type(e).__name__}: {e}") from e
