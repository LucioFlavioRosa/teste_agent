from interfaces.analysis_executor_interface import IAnalysisExecutor
from openai import OpenAI
import os

class OpenAILLMExecutor(IAnalysisExecutor):
    """
    Executor de análise baseado em LLM (OpenAI). Chave de API e cliente são injetados.
    """
    def __init__(self, openai_api_key: str, prompt_dir: str):
        if not openai_api_key:
            raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.prompt_dir = prompt_dir
        self._supported_analysis_types = self._descobrir_tipos_analise()

    def _descobrir_tipos_analise(self):
        # Descobre tipos de análise disponíveis a partir dos arquivos de prompt
        tipos = []
        try:
            for nome in os.listdir(self.prompt_dir):
                if nome.endswith('.md'):
                    tipos.append(nome.replace('.md', ''))
        except Exception:
            pass
        return tipos

    def get_supported_analysis_types(self):
        return self._supported_analysis_types

    def _carregar_prompt(self, tipo_analise: str) -> str:
        caminho_prompt = os.path.join(self.prompt_dir, f'{tipo_analise}.md')
        try:
            with open(caminho_prompt, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}")

    def execute_analysis(self, tipo_analise: str, codigo: str, analise_extra: str, model_name: str = None, max_token_out: int = None) -> str:
        prompt_sistema = self._carregar_prompt(tipo_analise)
        mensagens = [
            {"role": "system", "content": prompt_sistema},
            {'role': 'user', 'content': codigo},
            {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
        ]
        try:
            response = self.openai_client.chat.completions.create(
                model=model_name or 'gpt-4.1',
                messages=mensagens,
                temperature=0.5,
                max_tokens=max_token_out or 3000
            )
            conteudo_resposta = response.choices[0].message.content.strip()
            return conteudo_resposta
        except Exception as e:
            print(f"ERRO: Falha na chamada à API da OpenAI para análise '{tipo_analise}'. Causa: {e}")
            raise RuntimeError(f"Erro ao comunicar com a OpenAI: {e}") from e
