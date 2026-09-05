from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SpeechProvider(ABC):
    """Abstract interface defining the contract for Speech-to-Text translation providers."""

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> Dict[str, Any]:
        """Performs Speech-to-Text translation and returns the raw response dictionary."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verifies if the provider service endpoint is healthy and accessible."""
        pass

    @abstractmethod
    def supported_languages(self) -> List[str]:
        """Returns the list of ISO 639-1 language codes supported by this provider."""
        pass

    @abstractmethod
    def supported_formats(self) -> List[str]:
        """Returns the list of supported file mime types."""
        pass

    @abstractmethod
    def max_audio_length(self) -> int:
        """Returns the maximum audio length limit in seconds."""
        pass

    @abstractmethod
    def estimate_cost(self, duration_seconds: float) -> float:
        """Returns the estimated processing cost in USD."""
        pass
