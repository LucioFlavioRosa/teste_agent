import os
from typing import Dict
from interfaces.llm_client_interface import ILLMClient
from services.openai_client import OpenAIClient

class RevisorGeral:
    """Classe principal para execução de análises LLM com injeção de dependência."""
    
    def __init__(self, llm_client: ILLMClient = None):
        self.llm_client = llm_client or OpenAIClient()
    
    def carregar_prompt(self, tipo_analise: str) -> str:
        """Carrega o prompt específico para o tipo de análise.
        
        Args:
            tipo_analise: Tipo de análise
            
        Returns:
            str: Conteúdo do prompt
            
        Raises:
            ValueError: Se arquivo de prompt não encontrado
        """
        caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
        try:
            with open(caminho_prompt, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError as e:
            raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho_prompt}") from e
    
    def executar_analise_llm(
        self,
        tipo_analise: str,
        codigo: str,
        analise_extra: str,
        model_name: str,
        max_token_out: int
    ) -> str:
        """Executa análise usando LLM com injeção de dependência.
        
        Args:
            tipo_analise: Tipo de análise
            codigo: Código a ser analisado
            analise_extra: Instruções extras
            model_name: Nome do modelo LLM
            max_token_out: Máximo de tokens na saída
            
        Returns:
            str: Resultado da análise
            
        Raises:
            RuntimeError: Em caso de erro na comunicação com LLM
        """
        prompt_sistema = self.carregar_prompt(tipo_analise)
        mensagens = [
            {"role": "system", "content": prompt_sistema},
            {'role': 'user', 'content': codigo},
            {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
        ]
        
        try:
            return self.llm_client.chat_completion(
                messages=mensagens,
                model=model_name,
                temperature=0.5,
                max_tokens=max_token_out
            )
        except Exception as e:
            print(f"ERRO: Falha na chamada à API LLM para análise '{tipo_analise}'. Causa: {type(e).__name__}: {e}")
            raise RuntimeError(f"Erro ao comunicar com LLM: {type(e).__name__}: {e}") from e

# Função de compatibilidade para manter API existente
def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int
) -> str:
    """Função de compatibilidade para manter API existente."""
    revisor = RevisorGeral()
    return revisor.executar_analise_llm(tipo_analise, codigo, analise_extra, model_name, max_token_out)
