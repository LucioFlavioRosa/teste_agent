from domain.models.analise_request import AnaliseRequest
from domain.models.analise_response import AnaliseResponse

class ExecutarAnaliseUseCase:
    def __init__(self, prompt_loader_service, analise_orchestrator_service):
        self.prompt_loader_service = prompt_loader_service
        self.analise_orchestrator_service = analise_orchestrator_service

    def execute(self, analise_request: AnaliseRequest):
        conteudo = self.analise_orchestrator_service.executar_analise(analise_request)
        response = AnaliseResponse(
            conteudo=conteudo,
            modelo_utilizado=analise_request.model_name
        )
        return response
