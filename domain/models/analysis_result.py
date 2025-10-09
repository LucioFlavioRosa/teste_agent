class AnalysisResult:
    def __init__(self, analysis_type: str, result: str, metadata: dict):
        self.analysis_type = analysis_type
        self.result = result
        self.metadata = metadata
