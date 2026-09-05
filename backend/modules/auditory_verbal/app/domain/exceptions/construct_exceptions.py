class ConstructEngineException(Exception):
    """Base exception for Psychometric Construct Evaluation Engine errors."""

    pass


class ConstructEvaluationFailure(ConstructEngineException):
    def __init__(self, session_id: str, reason: str):
        super().__init__(f"Construct evaluation failed for session '{session_id}': {reason}")


class ConstructDefinitionMissing(ConstructEngineException):
    def __init__(self, construct_name: str):
        super().__init__(f"Construct definition for '{construct_name}' not found in repository.")


class EvaluationValidationFailure(ConstructEngineException):
    def __init__(self, eval_id: str, reason: str):
        super().__init__(f"Evaluation validation error for '{eval_id}': {reason}")


class InvalidConstructSchema(ConstructEngineException):
    def __init__(self, prompt_id: str, reason: str):
        super().__init__(f"Invalid output schema returned for construct evaluation prompt '{prompt_id}': {reason}")


class EvaluationPromptFailure(ConstructEngineException):
    def __init__(self, prompt_id: str, reason: str):
        super().__init__(f"APOS prompt execution failed for evaluation prompt '{prompt_id}': {reason}")


class BehavioralEvidenceMissing(ConstructEngineException):
    def __init__(self, session_id: str):
        super().__init__(f"No behavioral evidence items found for session '{session_id}'.")


class PsychometricEvaluationFailure(ConstructEngineException):
    def __init__(self, session_id: str, reason: str):
        super().__init__(f"Psychometric construct evaluation pipeline error for session '{session_id}': {reason}")
