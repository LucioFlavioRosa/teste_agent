import os
from interfaces.llm_service_interface import ILLMService
from services.openai_llm_service import OpenAILLMService
from services.prompt_loader import PromptLoader

class RevisorGeral:
    def __init__(self, llm_service: ILLMService = None):
        self.llm_service = llm_service or OpenAILLMService()
        self.prompt_loader = PromptLoader()
    
    def executar_analise_llm(self, tipo_analise: str, codigo: str, analise_extra: str, 
                           model_name: str, max_token_out: int) -> str:
        """Executa análise usando serviço LLM"""
        prompt_sistema = self.prompt_loader.carregar_prompt(tipo_analise)
        
        mensagens = [
            {"role": "system", "content": prompt_sistema},
            {'role': 'user', 'content': codigo},
            {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' 
             if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
        ]
        
        return self.llm_service.gerar_resposta(mensagens, model_name, max_token_out)

# Instância global para compatibilidade
_revisor_geral = RevisorGeral()

def executar_analise_llm(tipo_analise: str, codigo: str, analise_extra: str, 
                        model_name: str, max_token_out: int) -> str:
    """Função de compatibilidade para manter a interface existente"""
    return _revisor_geral.executar_analise_llm(tipo_analise, codigo, analise_extra, model_name, max_token_out)