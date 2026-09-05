from typing import List, Dict, Any
from app.infrastructure.speech.providers.base_provider import SpeechProvider


class WhisperProvider(SpeechProvider):
    """OpenAI Whisper Speech-to-Text provider integration."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> Dict[str, Any]:
        # Simulates OpenAI Whisper JSON response format
        return {
            "text": "Hello, welcome to MentiScope assessment engine.",
            "language": "en",
            "duration": 5.2,
            "segments": [
                {
                    "id": 0,
                    "seek": 0,
                    "start": 0.0,
                    "end": 5.2,
                    "text": "Hello, welcome to MentiScope assessment engine.",
                    "words": [
                        {"word": "Hello,", "start": 0.0, "end": 0.8, "probability": 0.98},
                        {"word": "welcome", "start": 0.8, "end": 1.5, "probability": 0.99},
                        {"word": "to", "start": 1.5, "end": 2.0, "probability": 0.95},
                        {"word": "MentiScope", "start": 2.0, "end": 3.2, "probability": 0.97},
                        {"word": "assessment", "start": 3.2, "end": 4.2, "probability": 0.99},
                        {"word": "engine.", "start": 4.2, "end": 5.2, "probability": 0.98},
                    ],
                }
            ],
            "api_latency": 150.0,
        }

    async def health_check(self) -> bool:
        return True

    def supported_languages(self) -> List[str]:
        return ["en", "es", "fr", "de", "it", "ja"]

    def supported_formats(self) -> List[str]:
        return ["audio/wav", "audio/mpeg", "audio/mp3"]

    def max_audio_length(self) -> int:
        return 1800  # 30 mins

    def estimate_cost(self, duration_seconds: float) -> float:
        # OpenAI Whisper API charges $0.006 / minute
        minutes = duration_seconds / 60.0
        return round(minutes * 0.006, 6)
