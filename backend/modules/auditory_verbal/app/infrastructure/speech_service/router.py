from typing import Dict, List, Optional
from app.infrastructure.speech_service.provider_interface import ISpeechProvider, MockSpeechProvider
from app.domain.exceptions.speech_exceptions import ProviderUnavailable
from app.core.logging import logger


class ProviderRouter:
    """Manages provider routing, capability matching, retries, and provider failover strategies."""

    def __init__(self, providers: Optional[List[ISpeechProvider]] = None):
        self.providers: List[ISpeechProvider] = providers or [MockSpeechProvider()]

    def select_provider(self, format_str: str = "audio/webm") -> ISpeechProvider:
        for p in self.providers:
            if p.health() and format_str in p.supported_formats():
                logger.info(f"[SPS ROUTER] Selected provider '{p.provider_name}'")
                return p

        raise ProviderUnavailable("All configured speech providers are unavailable or unsupported.")
