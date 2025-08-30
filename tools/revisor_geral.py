import os
from abc import ABC, abstractmethod
from typing import Dict, Optional
from google.colab import userdata
from openai import OpenAI

# Interfaces para DIP
class ILLMService(ABC):
    """Interface para serviços de LLM (DIP)."""
    
    @abstractmethod
    def generate_completion(self, messages: list, model_name: str, max_tokens: int, temperature: float) -> str:
        """Gera uma resposta usando o modelo de linguagem."""
        pass

class ICredentialProvider(ABC):
    """Interface para provedores de credenciais (DIP)."""
    
    @abstractmethod
    def get_credential(self, key: str) -> Optional[str]:
        """Obtém uma credencial pelo nome da chave."""
        pass

class IPromptLoader(ABC):
    """Interface para carregadores de prompt (DIP)."""
    
    @abstractmethod
    def load_prompt(self, analysis_type: str) -> str:
        """Carrega um prompt para o tipo de análise especificado."""
        pass

# Implementações concretas
class ColabCredentialProvider(ICredentialProvider):
    """Provedor de credenciais do Google Colab."""
    
    def get_credential(self, key: str) -> Optional[str]:
        """Obtém credencial do userdata do Colab."""
        try:
            return userdata.get(key)
        except Exception as e:
            raise ValueError(f"Erro ao obter credencial '{key}': {e}")

class OpenAIService(ILLMService):
    """Implementação do serviço OpenAI."""
    
    def __init__(self, credential_provider: ICredentialProvider):
        api_key = credential_provider.get_credential('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("A chave da API da OpenAI não foi encontrada.")
        
        self.client = OpenAI(api_key=api_key)
    
    def generate_completion(self, messages: list, model_name: str, max_tokens: int, temperature: float) -> str:
        """Gera resposta usando a API da OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"Erro ao comunicar com a OpenAI: {type(e).__name__}: {e}") from e

class FilePromptLoader(IPromptLoader):
    """Carregador de prompts baseado em arquivos."""
    
    def load_prompt(self, analysis_type: str) -> str:
        """Carrega prompt de arquivo no sistema de arquivos."""
        caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{analysis_type}.md')
        try:
            with open(caminho_prompt, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError as e:
            raise ValueError(f"Arquivo de prompt para a análise '{analysis_type}' não encontrado em: {caminho_prompt}") from e

class AnalysisService:
    """Serviço principal de análise com injeção de dependências."""
    
    def __init__(self, 
                 llm_service: ILLMService, 
                 prompt_loader: IPromptLoader):
        self.llm_service = llm_service
        self.prompt_loader = prompt_loader
    
    def executar_analise_llm(self,
                           tipo_analise: str,
                           codigo: str,
                           analise_extra: str,
                           model_name: str,
                           max_token_out: int) -> str:
        """Executa análise usando LLM com dependências injetadas."""
        
        # Carregar prompt
        prompt_sistema = self.prompt_loader.load_prompt(tipo_analise)
        
        # Preparar mensagens
        mensagens = [
            {"role": "system", "content": prompt_sistema},
            {'role': 'user', 'content': codigo},
            {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
        ]
        
        # Executar análise
        return self.llm_service.generate_completion(
            messages=mensagens,
            model_name=model_name,
            max_tokens=max_token_out,
            temperature=0.5
        )

# Configuração padrão para compatibilidade
_credential_provider = ColabCredentialProvider()
_llm_service = OpenAIService(_credential_provider)
_prompt_loader = FilePromptLoader()
_analysis_service = AnalysisService(_llm_service, _prompt_loader)

# Funções de compatibilidade
def carregar_prompt(tipo_analise: str) -> str:
    """Função de compatibilidade para carregar prompt."""
    return _prompt_loader.load_prompt(tipo_analise)

def executar_analise_llm(tipo_analise: str,
                        codigo: str,
                        analise_extra: str,
                        model_name: str,
                        max_token_out: int) -> str:
    """Função de compatibilidade para executar análise."""
    return _analysis_service.executar_analise_llm(
        tipo_analise=tipo_analise,
        codigo=codigo,
        analise_extra=analise_extra,
        model_name=model_name,
        max_token_out=max_token_out
    )