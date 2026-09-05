import os
from typing import Dict, List
from app.infrastructure.speech.providers.base_provider import SpeechProvider
from app.infrastructure.speech.providers.whisper_provider import WhisperProvider
from app.infrastructure.speech.providers.azure_provider import AzureSpeechProvider
from app.infrastructure.speech.providers.deepgram_provider import DeepgramProvider


class SpeechProviderRegistry:
    """Registry coordinating active SpeechProvider instances and reporting endpoint health statuses."""

    def __init__(self):
        self._providers: Dict[str, SpeechProvider] = {}
        # Pre-register built-in providers
        self.register("whisper", WhisperProvider())
        self.register("azure", AzureSpeechProvider())
        self.register("deepgram", DeepgramProvider())

    def register(self, name: str, provider: SpeechProvider) -> None:
        self._providers[name.lower()] = provider

    def get_provider(self, name: str) -> SpeechProvider:
        prov = self._providers.get(name.lower())
        if not prov:
            raise ValueError(f"Speech provider '{name}' is not registered.")
        return prov

    def get_default_provider(self) -> SpeechProvider:
        # Defaults to whisper or system configuration
        provider_name = os.getenv("SPEECH_PROVIDER", "whisper")
        return self.get_provider(provider_name)

    def list_providers(self) -> List[str]:
        return list(self._providers.keys())

    async def report_health(self) -> Dict[str, bool]:
        report = {}
        for name, prov in self._providers.items():
            try:
                report[name] = await prov.health_check()
            except Exception:
                report[name] = False
        return report


# Global registry instance
speech_registry = SpeechProviderRegistry()
