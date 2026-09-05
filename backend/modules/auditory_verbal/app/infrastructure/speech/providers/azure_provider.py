from typing import List, Dict, Any
from app.infrastructure.speech.providers.base_provider import SpeechProvider


class AzureSpeechProvider(SpeechProvider):
    """Microsoft Azure Speech-to-Text translation provider integration."""

    def __init__(self, subscription_key: str = "", region: str = "eastus"):
        self.subscription_key = subscription_key
        self.region = region

    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> Dict[str, Any]:
        # Simulates Azure Speech Services JSON response format
        return {
            "DisplayText": "Hello, welcome to MentiScope assessment engine.",
            "RecognitionStatus": "Success",
            "Offset": 0,
            "Duration": 52000000,  # 100ns units -> 5.2s
            "NBest": [
                {
                    "Confidence": 0.975,
                    "Lexical": "hello welcome to mentiscope assessment engine",
                    "Words": [
                        {"Word": "hello", "Offset": 0, "Duration": 8000000, "Confidence": 0.98},
                        {"Word": "welcome", "Offset": 8000000, "Duration": 7000000, "Confidence": 0.99},
                        {"Word": "to", "Offset": 15000000, "Duration": 5000000, "Confidence": 0.95},
                        {"Word": "mentiscope", "Offset": 20000000, "Duration": 12000000, "Confidence": 0.97},
                        {"Word": "assessment", "Offset": 32000000, "Duration": 10000000, "Confidence": 0.99},
                        {"Word": "engine", "Offset": 42000000, "Duration": 10000000, "Confidence": 0.98},
                    ],
                }
            ],
            "api_latency": 120.0,
        }

    async def health_check(self) -> bool:
        return True

    def supported_languages(self) -> List[str]:
        return ["en", "es", "fr", "de", "zh-cn"]

    def supported_formats(self) -> List[str]:
        return ["audio/wav", "audio/ogg", "audio/mp3"]

    def max_audio_length(self) -> int:
        return 3600  # 1 hour

    def estimate_cost(self, duration_seconds: float) -> float:
        # Azure Speech charges $1.00 per hour
        hours = duration_seconds / 3600.0
        return round(hours * 1.00, 6)
