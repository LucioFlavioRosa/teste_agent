from infrastructure.llm.openai_client import OpenAIClient
from infrastructure.config.llm_config import DEFAULT_MODEL, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE
from domain.services.prompt_loader_service import PromptLoaderService
from domain.services.analise_orchestrator_service import AnaliseOrchestratorService
from domain.models.analise_request import AnaliseRequest
from application.use_cases.executar_analise_use_case import ExecutarAnaliseUseCase

openai_client = OpenAIClient()
prompt_loader_service = PromptLoaderService()
analise_orchestrator_service = AnaliseOrchestratorService(prompt_loader_service, openai_client)
executar_analise_use_case = ExecutarAnaliseUseCase(prompt_loader_service, analise_orchestrator_service)

def executar_analise_llm(tipo_analise, codigo, analise_extra, model_name=DEFAULT_MODEL, max_token_out=DEFAULT_MAX_TOKENS, temperature=DEFAULT_TEMPERATURE):
    analise_request = AnaliseRequest(
        tipo_analise=tipo_analise,
        codigo=codigo,
        analise_extra=analise_extra,
        model_name=model_name,
        max_token_out=max_token_out,
        temperature=temperature
    )
    response = executar_analise_use_case.execute(analise_request)
    return response.conteudo
