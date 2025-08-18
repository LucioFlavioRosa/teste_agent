import os
import asyncio
from openai import OpenAI, AsyncOpenAI
from typing import Dict
from google.colab import userdata


OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
async_openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

def carregar_prompt(tipo_analise: str) -> str:
    """Carrega o conteúdo do arquivo de prompt correspondente."""
    caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")

async def executar_analise_llm_async(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int
) -> str:
    """Versão assíncrona da função de análise LLM"""
    prompt_sistema = carregar_prompt(tipo_analise)

    mensagens = [
        {"role": "system", "content": prompt_sistema},
        {'role': 'user', 'content': codigo},
        {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
    ]

    try:
        response = await async_openai_client.chat.completions.create(
            model=model_name,
            messages=mensagens,
            temperature=0.5,
            max_tokens=max_token_out
        )
        conteudo_resposta = response.choices[0].message.content.strip()
        return conteudo_resposta
        
    except Exception as e:
        print(f"ERRO: Falha na chamada à API da OpenAI para análise '{tipo_analise}'. Causa: {e}")
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {e}") from e

def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int
) -> str:
    """Versão síncrona da função de análise LLM (mantida para compatibilidade)"""
    
    prompt_sistema = carregar_prompt(tipo_analise)

    mensagens = [
        {"role": "system", "content": prompt_sistema},
        {'role': 'user', 'content': codigo},
        {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
    ]

    try:
        # Verificar se estamos em um ambiente que suporta asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Se já estamos em um loop de eventos, use a versão síncrona
                response = openai_client.chat.completions.create(
                    model=model_name,
                    messages=mensagens,
                    temperature=0.5,
                    max_tokens=max_token_out
                )
                conteudo_resposta = response.choices[0].message.content.strip()
            else:
                # Se não estamos em um loop de eventos, podemos usar a versão assíncrona
                conteudo_resposta = asyncio.run(executar_analise_llm_async(
                    tipo_analise, codigo, analise_extra, model_name, max_token_out
                ))
        except RuntimeError:
            # Fallback para versão síncrona se houver problemas com asyncio
            response = openai_client.chat.completions.create(
                model=model_name,
                messages=mensagens,
                temperature=0.5,
                max_tokens=max_token_out
            )
            conteudo_resposta = response.choices[0].message.content.strip()
            
        return conteudo_resposta
        
    except Exception as e:
        print(f"ERRO: Falha na chamada à API da OpenAI para análise '{tipo_analise}'. Causa: {e}")
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {e}") from e