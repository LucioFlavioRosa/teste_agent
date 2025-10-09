from domain/models.analysis_request import AnalysisRequest
from domain/models.analysis_result import AnalysisResult

class AnalyzeCodeUseCase:
    def __init__(self, code_analysis_service):
        self.code_analysis_service = code_analysis_service

    def execute(self, request: AnalysisRequest) -> AnalysisResult:
        return self.code_analysis_service.analyze_code(request)
