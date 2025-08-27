import os
from openai import OpenAI
from typing import Dict
from core.config_provider import ConfigFactory, ConfigProvider

class RevisorGeral:
    """Classe responsável pela execução de análises via LLM."""
    
    def __init__(self, config_provider: ConfigProvider = None):
        self.config_provider = config_provider or ConfigFactory.create_provider()
        self.openai_client = OpenAI(api_key=self.config_provider.get_openai_api_key())
    
    def carregar_prompt(self, tipo_analise: str) -> str:
        """Carrega o prompt específico para o tipo de análise."""
        caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
        try:
            with open(caminho_prompt, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError as e:
            raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}") from e
    
    def executar_analise_llm(self,
                            tipo_analise: str,
                            codigo: str,
                            analise_extra: str,
                            model_name: str,
                            max_token_out: int) -> str:
        """Executa a análise usando o LLM."""
        prompt_sistema = self.carregar_prompt(tipo_analise)
        mensagens = [
            {"role": "system", "content": prompt_sistema},
            {'role': 'user', 'content': codigo},
            {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
        ]
        try:
            response = self.openai_client.chat.completions.create(
                model=model_name,
                messages=mensagens,
                temperature=0.5,
                max_tokens=max_token_out
            )
            conteudo_resposta = response.choices[0].message.content.strip()
            return conteudo_resposta
        except Exception as e:
            print(f"ERRO: Falha na chamada à API da OpenAI para análise '{tipo_analise}'. Causa: {type(e).__name__}: {e}")
            raise RuntimeError(f"Erro ao comunicar com a OpenAI: {type(e).__name__}: {e}") from e

# Instância global para compatibilidade
_revisor_geral = RevisorGeral()

def executar_analise_llm(tipo_analise: str,
                        codigo: str,
                        analise_extra: str,
                        model_name: str,
                        max_token_out: int) -> str:
    """Função de compatibilidade que delega para a instância da classe."""
    return _revisor_geral.executar_analise_llm(
        tipo_analise=tipo_analise,
        codigo=codigo,
        analise_extra=analise_extra,
        model_name=model_name,
        max_token_out=max_token_out
    )