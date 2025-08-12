from openai import OpenAI
from google.colab import userdata

class LLMClient:
    """Cliente para integração com OpenAI, desacoplado para facilitar testes."""
    def __init__(self):
        self._openai_api_key = userdata.get('OPENAI_API_KEY')
        if not self._openai_api_key:
            raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")
        self._client = OpenAI(api_key=self._openai_api_key)

    def get_openai_client(self):
        return self._client

    def executar_analise_llm(self, tipo_analise, codigo, analise_extra, model_name, max_token_out):
        from tools.revisor_geral import carregar_prompt
        prompt_sistema = carregar_prompt(tipo_analise)
        mensagens = [
            {"role": "system", "content": prompt_sistema},
            {'role': 'user', 'content': codigo},
            {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
        ]
        response = self._client.chat.completions.create(
            model=model_name,
            messages=mensagens,
            temperature=0.5,
            max_tokens=max_token_out
        )
        return response.choices[0].message.content.strip()
