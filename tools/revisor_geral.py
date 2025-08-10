import openai


def carregar_prompt(tipo_analise):
    """
    Carrega o prompt correspondente ao tipo de análise.
    Args:
        tipo_analise (str): Tipo de análise.
    Returns:
        str: Prompt carregado.
    """
    # Exemplo: carregar de arquivo ou dicionário
    prompts = {
        'qualidade': 'Analise a qualidade do código...'
    }
    return prompts.get(tipo_analise, '')


def construir_mensagens(repositorio, codigo, prompt):
    """
    Constrói as mensagens para o modelo LLM.
    Args:
        repositorio (str): Nome do repositório.
        codigo (dict): Dicionário de arquivos e conteúdos.
        prompt (str): Prompt base.
    Returns:
        list: Lista de mensagens para o modelo.
    """
    mensagens = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Repositório: {repositorio}. Código: {list(codigo.keys())}"}
    ]
    return mensagens


def executar_analise_llm(tipo_analise, repositorio, codigo, openai_client=None):
    """
    Executa a análise LLM usando o cliente OpenAI.
    Args:
        tipo_analise (str): Tipo de análise.
        repositorio (str): Nome do repositório.
        codigo (dict): Dicionário de arquivos e conteúdos.
        openai_client (module, opcional): Cliente OpenAI injetável para testes.
    Returns:
        dict: Resultado da análise.
    """
    prompt = carregar_prompt(tipo_analise)
    mensagens = construir_mensagens(repositorio, codigo, prompt)
    client = openai_client if openai_client else openai
    resposta = client.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=mensagens
    )
    return {"resposta": resposta.choices[0].message['content']}
