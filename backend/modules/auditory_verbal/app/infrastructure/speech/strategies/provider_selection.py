from typing import Dict, Tuple
from app.infrastructure.speech.providers.base_provider import SpeechProvider
from app.infrastructure.speech.providers.provider_registry import speech_registry


class ProviderSelectionStrategy:
    """Strategy class resolving the target STT provider based on custom operational policies."""

    @staticmethod
    def resolve_provider(policy: str = "DEFAULT", duration_seconds: float = 0.0) -> Tuple[str, SpeechProvider]:
        """Resolves target SpeechProvider by applying selected policy checks."""
        policy = policy.upper()

        if policy == "LOWEST_COST":
            # Compare estimated transcription cost for the duration
            cheapest_name = "whisper"
            cheapest_cost = float("inf")
            for name in speech_registry.list_providers():
                prov = speech_registry.get_provider(name)
                cost = prov.estimate_cost(duration_seconds)
                if cost < cheapest_cost:
                    cheapest_cost = cost
                    cheapest_name = name
            return cheapest_name, speech_registry.get_provider(cheapest_name)

        elif policy == "FASTEST":
            # Deepgram is typically resolved as the fastest mock provider latency
            return "deepgram", speech_registry.get_provider("deepgram")

        elif policy == "HIGHEST_AVAILABILITY":
            # Simple availability fallback logic: return whisper if available
            return "whisper", speech_registry.get_provider("whisper")

        else:
            # Default lookup
            import os
            default_name = os.getenv("SPEECH_PROVIDER", "whisper")
            return default_name, speech_registry.get_default_provider()


from typing import Tuple
