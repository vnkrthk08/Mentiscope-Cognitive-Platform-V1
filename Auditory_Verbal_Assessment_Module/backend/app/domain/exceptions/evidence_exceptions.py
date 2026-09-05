class EvidenceEngineException(Exception):
    """Base exception for Behavioral Evidence Extraction Engine errors."""

    pass


class TranscriptMissing(EvidenceEngineException):
    def __init__(self, session_id: str):
        super().__init__(f"No valid transcript found in SpeechProcessingResult for session '{session_id}'.")


class EvidenceExtractionFailure(EvidenceEngineException):
    def __init__(self, session_id: str, reason: str):
        super().__init__(f"Behavioral evidence extraction failed for session '{session_id}': {reason}")


class EvidenceValidationFailure(EvidenceEngineException):
    def __init__(self, evidence_id: str, reason: str):
        super().__init__(f"Evidence validation error for item '{evidence_id}': {reason}")


class ConstructNotFound(EvidenceEngineException):
    def __init__(self, construct_name: str):
        super().__init__(f"Target construct '{construct_name}' is not recognized in system Construct Repository.")


class InvalidEvidenceSchema(EvidenceEngineException):
    def __init__(self, prompt_id: str, reason: str):
        super().__init__(f"Extracted AI output schema invalid for prompt '{prompt_id}': {reason}")


class PromptExecutionFailure(EvidenceEngineException):
    def __init__(self, prompt_id: str, reason: str):
        super().__init__(f"APOS prompt execution failed for prompt '{prompt_id}': {reason}")


class BehavioralEvidenceFailure(EvidenceEngineException):
    def __init__(self, session_id: str, reason: str):
        super().__init__(f"Behavioral evidence pipeline failure for session '{session_id}': {reason}")
