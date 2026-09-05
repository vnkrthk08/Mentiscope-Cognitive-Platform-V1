from abc import ABC, abstractmethod
from typing import Any, Dict


class ISpeechService(ABC):
    """Abstract interface for Speech-to-Text and Acoustic Analysis service (Whisper, Deepgram adapters)."""

    @abstractmethod
    async def transcribe_audio(
        self, audio_bytes: bytes, filename: str
    ) -> Dict[str, Any]:
        """Convert audio file bytes to text transcript and acoustic metadata."""
        pass
