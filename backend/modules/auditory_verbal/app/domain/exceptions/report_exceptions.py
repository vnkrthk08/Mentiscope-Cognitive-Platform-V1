class ReportingEngineException(Exception):
    """Base exception for Assessment Reporting & Explainability Engine errors."""

    pass


class ReportGenerationFailure(ReportingEngineException):
    def __init__(self, session_id: str, reason: str):
        super().__init__(f"Assessment report generation failed for session '{session_id}': {reason}")


class MissingAssessmentData(ReportingEngineException):
    def __init__(self, session_id: str, data_name: str):
        super().__init__(f"Required assessment data '{data_name}' missing for session '{session_id}'.")


class MissingConstructExplanation(ReportingEngineException):
    def __init__(self, construct_name: str):
        super().__init__(f"Construct explanation missing for '{construct_name}'.")


class MissingEvidenceReference(ReportingEngineException):
    def __init__(self, evidence_id: str):
        super().__init__(f"Traceability evidence reference '{evidence_id}' missing or broken.")


class ExplainabilityFailure(ReportingEngineException):
    def __init__(self, session_id: str, reason: str):
        super().__init__(f"Explainability metadata aggregation failed for session '{session_id}': {reason}")


class ReportValidationFailure(ReportingEngineException):
    def __init__(self, report_id: str, reason: str):
        super().__init__(f"Assessment report validation error for report '{report_id}': {reason}")
