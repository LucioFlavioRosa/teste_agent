from infrastructure.llm.llm_client_interface import ILLMClient
from infrastructure.storage.prompt_repository_interface import IPromptRepository
from services.message_builder import MessageBuilder

class CodeAnalysisService:
    def __init__(self, llm_client: ILLMClient, prompt_repository: IPromptRepository):
        self.llm_client = llm_client
        self.prompt_repository = prompt_repository

    def analyze(self, tipo_analise: str, codigo: str, analise_extra: str, config):
        prompt_sistema = self.prompt_repository.get_prompt(tipo_analise)
        messages = MessageBuilder.build_messages(prompt_sistema, codigo, analise_extra)
        resposta = self.llm_client.chat_completion(
            messages=messages,
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
        return resposta
