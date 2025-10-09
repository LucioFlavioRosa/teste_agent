from typing import Any, Dict

class AnalysisResult:
    def __init__(self, analysis_type: str, findings: Any, metadata: Dict[str, Any]):
        self.analysis_type = analysis_type
        self.findings = findings
        self.metadata = metadata
