from typing import Dict, Any, List
from app.domain.exceptions.speaking_exceptions import (
    RecordingNotFound,
    RecordingTooShort,
    RecordingTooLong,
    InvalidRecordingFormat,
    RecordingValidationFailure,
)


class RecordingValidator:
    """Basic deterministic validator for captured voice recording files and metadata (Zero AI!)."""

    SUPPORTED_FORMATS: List[str] = ["audio/webm", "audio/wav", "audio/mp3", "audio/m4a"]

    def validate_recording(
        self,
        recording_meta: Dict[str, Any],
        min_duration_seconds: float = 2.0,
        max_duration_seconds: float = 300.0,
    ) -> bool:
        file_url = recording_meta.get("file_url")
        if not file_url:
            raise RecordingNotFound("EMPTY_URL")

        duration = recording_meta.get("duration_seconds", 0.0)
        if duration < min_duration_seconds:
            raise RecordingTooShort(duration, min_duration_seconds)
        if duration > max_duration_seconds:
            raise RecordingTooLong(duration, max_duration_seconds)

        fmt = recording_meta.get("format", "")
        if fmt not in self.SUPPORTED_FORMATS:
            raise InvalidRecordingFormat(fmt, self.SUPPORTED_FORMATS)

        file_size = recording_meta.get("file_size_bytes", 0)
        if file_size <= 0:
            raise RecordingValidationFailure("Captured recording file size is 0 bytes.")

        return True
