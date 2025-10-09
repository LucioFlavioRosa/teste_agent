class AnalysisRequestValidator:
    def validate(self, request):
        errors = []
        if not request.analysis_type:
            errors.append("O parâmetro 'analysis_type' é obrigatório.")
        if not request.code_source:
            errors.append("O parâmetro 'code_source' é obrigatório.")
        if not request.model_name:
            errors.append("O parâmetro 'model_name' é obrigatório.")
        if not request.max_tokens:
            errors.append("O parâmetro 'max_tokens' é obrigatório.")
        return errors
