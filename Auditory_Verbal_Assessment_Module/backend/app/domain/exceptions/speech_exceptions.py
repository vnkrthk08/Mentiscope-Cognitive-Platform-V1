class SpeechProcessingException(Exception):
    """Base exception for Speech Processing Service errors."""

    pass


class RecordingLoadFailure(SpeechProcessingException):
    def __init__(self, file_url: str, reason: str):
        super().__init__(f"Failed to load audio recording from '{file_url}': {reason}")


class UnsupportedAudioFormat(SpeechProcessingException):
    def __init__(self, format_str: str, supported: list):
        super().__init__(f"Unsupported audio format '{format_str}' for speech transcription. Supported: {', '.join(supported)}.")


class AudioValidationFailure(SpeechProcessingException):
    def __init__(self, reason: str):
        super().__init__(f"Speech audio validation failed: {reason}")


class ProviderUnavailable(SpeechProcessingException):
    def __init__(self, provider_name: str):
        super().__init__(f"Speech provider '{provider_name}' is currently unavailable or unhealthy.")


class ProviderTimeout(SpeechProcessingException):
    def __init__(self, provider_name: str, timeout_sec: float):
        super().__init__(f"Speech provider '{provider_name}' request timed out after {timeout_sec:.1f}s.")


class TranscriptionFailure(SpeechProcessingException):
    def __init__(self, provider_name: str, reason: str):
        super().__init__(f"Transcription failed on provider '{provider_name}': {reason}")


class TranscriptValidationFailure(SpeechProcessingException):
    def __init__(self, reason: str):
        super().__init__(f"Transcript output validation error: {reason}")


class SpeechProcessingFailure(SpeechProcessingException):
    def __init__(self, session_id: str, reason: str):
        super().__init__(f"Speech processing pipeline failed for session '{session_id}': {reason}")
