from abc import ABC, abstractmethod
from typing import Any, Dict, List
from app.domain.value_objects.enums import ProviderType


class ISpeechProvider(ABC):
    """Abstract interface for all speech-to-text providers (Whisper, Deepgram, Azure, Mock)."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Transcribes audio payload and returns standardized raw transcription dictionary."""
        pass

    @abstractmethod
    def health(self) -> bool:
        """Checks if provider endpoint is accessible and healthy."""
        pass

    @abstractmethod
    def supported_languages(self) -> List[str]:
        """Returns list of supported ISO language codes."""
        pass

    @abstractmethod
    def supported_formats(self) -> List[str]:
        """Returns list of supported audio MIME formats."""
        pass


class MockSpeechProvider(ISpeechProvider):
    """Deterministic Mock Speech Provider for unit testing and offline development."""

    @property
    def provider_name(self) -> str:
        return ProviderType.WHISPER.value

    def health(self) -> bool:
        return True

    def supported_languages(self) -> List[str]:
        return ["en-US", "en-GB", "en-IN"]

    def supported_formats(self) -> List[str]:
        return ["audio/webm", "audio/wav", "audio/mp3", "audio/m4a"]

    async def transcribe(self, audio_bytes: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        prompt_id = metadata.get("prompt_id", "UNKNOWN")

        # Deterministic mock transcripts per prompt
        mock_transcripts = {
            "S_P1": "Our team must prioritize safety protocols and address the logistics disruption immediately by re-routing medical supplies.",
            "S_P2": "We prioritized medical supplies over commercial goods because public health and ethical responsibility outweigh financial penalties.",
        }

        full_text = mock_transcripts.get(
            prompt_id, "Candidate provided a clear and structured oral response explaining the decision rationale."
        )

        words = full_text.split()
        word_timestamps = []
        current_time = 0.5

        for idx, w in enumerate(words):
            word_timestamps.append({
                "word": w.strip(".,"),
                "start_time": round(current_time, 2),
                "end_time": round(current_time + 0.4, 2),
                "confidence": 0.98,
            })
            current_time += 0.5

        return {
            "text": full_text,
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": round(current_time, 2),
                    "text": full_text,
                    "confidence": 0.96,
                }
            ],
            "word_timestamps": word_timestamps,
            "language": "en-US",
            "overall_confidence": 0.96,
            "provider_name": "MockWhisperEngine",
            "provider_version": "1.0.0",
            "model_version": "whisper-large-v3-mock",
        }
