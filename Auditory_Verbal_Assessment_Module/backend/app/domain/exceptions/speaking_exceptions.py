class SpeakingEngineException(Exception):
    """Base exception for Speaking Assessment Engine errors."""

    pass


class SpeakingModuleMissing(SpeakingEngineException):
    def __init__(self, scenario_id: str):
        super().__init__(f"Scenario '{scenario_id}' is missing a valid speaking module configuration.")


class RecordingInitializationFailure(SpeakingEngineException):
    def __init__(self, device_id: str, reason: str):
        super().__init__(f"Failed to initialize audio recording device '{device_id}': {reason}")


class RecordingFailure(SpeakingEngineException):
    def __init__(self, prompt_id: str, reason: str):
        super().__init__(f"Recording error for prompt '{prompt_id}': {reason}")


class RecordingNotFound(SpeakingEngineException):
    def __init__(self, recording_url: str):
        super().__init__(f"Recording file not found at reference: '{recording_url}'.")


class InvalidRecordingFormat(SpeakingEngineException):
    def __init__(self, format_str: str, supported: list):
        super().__init__(f"Unsupported recording format '{format_str}'. Supported formats: {', '.join(supported)}.")


class RecordingTooShort(SpeakingEngineException):
    def __init__(self, duration: float, min_required: float):
        super().__init__(f"Recording duration ({duration:.1f}s) is below minimum threshold of {min_required:.1f}s.")


class RecordingTooLong(SpeakingEngineException):
    def __init__(self, duration: float, max_allowed: float):
        super().__init__(f"Recording duration ({duration:.1f}s) exceeds maximum allowed limit of {max_allowed:.1f}s.")


class RecordingValidationFailure(SpeakingEngineException):
    def __init__(self, reason: str):
        super().__init__(f"Recording validation failed: {reason}")


class PromptNotFound(SpeakingEngineException):
    def __init__(self, prompt_id: str, scenario_id: str):
        super().__init__(f"Speaking prompt '{prompt_id}' not found in scenario '{scenario_id}'.")


class SpeakingSessionFailure(SpeakingEngineException):
    def __init__(self, session_id: str, reason: str):
        super().__init__(f"Speaking assessment session '{session_id}' failed: {reason}")
