class AnalysisRequestValidator:
    def __init__(self, valid_types):
        self.valid_types = valid_types

    def validate(self, request):
        errors = []
        if request.analysis_type not in self.valid_types:
            errors.append(f"Tipo de análise '{request.analysis_type}' inválido.")
        if not hasattr(request, 'code_source') or request.code_source is None:
            errors.append("Fonte de código não especificada.")
        return errors
