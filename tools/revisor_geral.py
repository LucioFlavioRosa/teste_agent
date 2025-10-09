from infrastructure.llm.openai_client_adapter import OpenAIClientAdapter
from infrastructure.storage.file_prompt_repository import FilePromptRepository
from config.llm_config import LLMConfig
from services.code_analysis_service import CodeAnalysisService

openai_client_adapter = OpenAIClientAdapter()
prompt_repository = FilePromptRepository()
code_analysis_service = CodeAnalysisService(openai_client_adapter, prompt_repository)

def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int
) -> str:
    config = LLMConfig(model_name=model_name, temperature=0.5, max_tokens=max_token_out)
    return code_analysis_service.analyze(tipo_analise, codigo, analise_extra, config)
