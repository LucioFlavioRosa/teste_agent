import os
from typing import Dict
from google.colab import userdata
from config.llm_config import LLMConfig
from infrastructure.llm.openai_client_adapter import OpenAIClientAdapter
from infrastructure.storage.file_prompt_repository import FilePromptRepository
from services.code_analysis_service import CodeAnalysisService

OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")

llm_config = LLMConfig.from_env()
llm_client = OpenAIClientAdapter(api_key=OPENAI_API_KEY)
prompt_repository = FilePromptRepository()
code_analysis_service = CodeAnalysisService(llm_client, prompt_repository)

def executar_analise_llm(tipo_analise: str, codigo: str, analise_extra: str) -> str:
    return code_analysis_service.analyze(tipo_analise, codigo, analise_extra, llm_config)
