from typing import List, Dict, Any
from app.infrastructure.speech.providers.base_provider import SpeechProvider


class DeepgramProvider(SpeechProvider):
    """Deepgram Speech-to-Text API translation provider integration."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> Dict[str, Any]:
        # Simulates Deepgram JSON response format
        return {
            "results": {
                "channels": [
                    {
                        "alternatives": [
                            {
                                "transcript": "Hello, welcome to MentiScope assessment engine.",
                                "confidence": 0.985,
                                "words": [
                                    {"word": "hello", "start": 0.0, "end": 0.8, "confidence": 0.98},
                                    {"word": "welcome", "start": 0.8, "end": 1.5, "confidence": 0.99},
                                    {"word": "to", "start": 1.5, "end": 2.0, "confidence": 0.95},
                                    {"word": "mentiscope", "start": 2.0, "end": 3.2, "confidence": 0.97},
                                    {"word": "assessment", "start": 3.2, "end": 4.2, "confidence": 0.99},
                                    {"word": "engine", "start": 4.2, "end": 5.2, "confidence": 0.98},
                                ],
                            }
                        ]
                    }
                ]
            },
            "metadata": {
                "duration": 5.2,
                "request_id": "dg-req-123456",
            },
            "api_latency": 95.0,
        }

    async def health_check(self) -> bool:
        return True

    def supported_languages(self) -> List[str]:
        return ["en", "es", "fr", "de", "hi", "it"]

    def supported_formats(self) -> List[str]:
        return ["audio/wav", "audio/mpeg", "audio/mp3", "audio/webm"]

    def max_audio_length(self) -> int:
        return 7200  # 2 hours

    def estimate_cost(self, duration_seconds: float) -> float:
        # Deepgram charges $0.0125 per minute (Nova-2 model)
        minutes = duration_seconds / 60.0
        return round(minutes * 0.0125, 6)
