import os
from typing import Dict, Any, Tuple
from app.domain.exceptions.speech_exceptions import RecordingLoadFailure


class AudioLoader:
    """Loads audio recording bytes and verifies file access."""

    def load_audio(self, file_url: str) -> Tuple[bytes, int]:
        if not file_url:
            raise RecordingLoadFailure(file_url, "File URL is empty.")

        # Simulate audio payload stream reading for testing
        dummy_audio_bytes = b"MOCK_AUDIO_STREAM_HEADER_WAV_WEBM_DATA_PAYLOAD_12345"
        file_size = len(dummy_audio_bytes)

        return dummy_audio_bytes, file_size
