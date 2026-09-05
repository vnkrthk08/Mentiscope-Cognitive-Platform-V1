class ScoringEngineException(Exception):
    """Base exception for Psychometric Scoring & Decision Engine errors."""

    pass


class ScoringFailure(ScoringEngineException):
    def __init__(self, session_id: str, reason: str):
        super().__init__(f"Psychometric scoring failed for session '{session_id}': {reason}")


class NormalizationFailure(ScoringEngineException):
    def __init__(self, construct_name: str, raw_score: float):
        super().__init__(f"Failed to normalize raw score {raw_score} for construct '{construct_name}'.")


class CalibrationFailure(ScoringEngineException):
    def __init__(self, model_version: str, reason: str):
        super().__init__(f"Score calibration model '{model_version}' failed: {reason}")


class WeightCalculationFailure(ScoringEngineException):
    def __init__(self, construct_name: str, reason: str):
        super().__init__(f"Weight calculation failed for construct '{construct_name}': {reason}")


class ReliabilityFailure(ScoringEngineException):
    def __init__(self, session_id: str, reason: str):
        super().__init__(f"Reliability estimation failed for session '{session_id}': {reason}")


class DecisionFailure(ScoringEngineException):
    def __init__(self, session_id: str, reason: str):
        super().__init__(f"Assessment decision generation failed for session '{session_id}': {reason}")


class AssessmentScoreValidationFailure(ScoringEngineException):
    def __init__(self, score_id: str, reason: str):
        super().__init__(f"Assessment score validation failed for score item '{score_id}': {reason}")
