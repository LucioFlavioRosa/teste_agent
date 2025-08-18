"""Módulo de execução de análises via LLM da OpenAI.

Este módulo fornece funcionalidades para carregar prompts de análise e
executar análises de código utilizando a API da OpenAI.

Dependências:
  - openai: Para comunicação com a API da OpenAI
  - google.colab.userdata: Para obtenção segura da chave de API da OpenAI

A configuração da API da OpenAI é feita através de uma chave armazenada
no google.colab.userdata, evitando exposição de credenciais no código.
"""

import os
from openai import OpenAI
from typing import Dict
from google.colab import userdata


OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

def carregar_prompt(tipo_analise: str) -> str:
    """Carrega o conteúdo do arquivo de prompt correspondente.
    
    Args:
        tipo_analise: Nome do tipo de análise que corresponde ao arquivo de prompt.
        
    Returns:
        String contendo o conteúdo do arquivo de prompt.
        
    Raises:
        ValueError: Se o arquivo de prompt para o tipo de análise não for encontrado.
    """
    caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")

def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int
) -> str:
    """Executa uma análise de código utilizando a API da OpenAI.
    
    Carrega o prompt específico para o tipo de análise solicitado e envia
    o código junto com instruções extras para o modelo LLM da OpenAI.
    
    Args:
        tipo_analise: Tipo de análise a ser realizada, deve corresponder a um arquivo de prompt.
        codigo: Código-fonte a ser analisado.
        analise_extra: Instruções adicionais para a análise.
        model_name: Nome do modelo LLM da OpenAI a ser utilizado.
        max_token_out: Limite máximo de tokens na resposta.
        
    Returns:
        String contendo o resultado da análise gerado pelo modelo LLM.
        
    Raises:
        ValueError: Se o arquivo de prompt para o tipo de análise não for encontrado.
        RuntimeError: Se ocorrer falha na comunicação com a API da OpenAI.
    """
    
    
    prompt_sistema = carregar_prompt(tipo_analise)

    mensagens = [
        {"role": "system", "content": prompt_sistema},
        {'role': 'user', 'content': codigo},
        {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
    ]

    try:
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