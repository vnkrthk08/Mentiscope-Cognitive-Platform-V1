from typing import Dict, Any, List
from app.domain.exceptions.speech_exceptions import UnsupportedAudioFormat, AudioValidationFailure


class AudioValidator:
    """Validates recording payload integrity, metadata consistency, and format support."""

    SUPPORTED_FORMATS: List[str] = ["audio/webm", "audio/wav", "audio/mp3", "audio/m4a"]

    def validate(self, metadata: Dict[str, Any]) -> bool:
        file_url = metadata.get("file_url")
        if not file_url:
            raise AudioValidationFailure("Missing 'file_url' in recording metadata.")

        fmt = metadata.get("format", "audio/webm")
        if fmt not in self.SUPPORTED_FORMATS:
            raise UnsupportedAudioFormat(fmt, self.SUPPORTED_FORMATS)

        duration = metadata.get("duration_seconds", 0.0)
        if duration <= 0.0:
            raise AudioValidationFailure(f"Invalid recording duration: {duration}s")

        return True
