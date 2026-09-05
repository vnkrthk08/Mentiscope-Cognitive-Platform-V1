import os
from typing import Dict, List
from app.infrastructure.prompt.providers.base_provider import LLMProvider
from app.infrastructure.prompt.providers.openai_provider import OpenAIProvider
from app.infrastructure.prompt.providers.claude_provider import ClaudeProvider
from app.infrastructure.prompt.providers.gemini_provider import GeminiProvider
from app.infrastructure.prompt.providers.openrouter_provider import OpenRouterProvider
from app.infrastructure.prompt.providers.mock_provider import MockProvider


class LLMProviderRegistry:
    """Registry coordinating active LLMProvider instances."""

    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {}
        # Pre-register built-in providers
        self.register("openai", OpenAIProvider())
        self.register("claude", ClaudeProvider())
        self.register("gemini", GeminiProvider())
        self.register("openrouter", OpenRouterProvider())
        self.register("nvidia", OpenRouterProvider())
        self.register("mock", MockProvider())

    def register(self, name: str, provider: LLMProvider) -> None:
        self._providers[name.lower()] = provider

    def get_provider(self, name: str) -> LLMProvider:
        prov = self._providers.get(name.lower())
        if not prov:
            raise ValueError(f"LLM Provider '{name}' is not registered.")
        return prov

    def get_default_provider(self) -> LLMProvider:
        from app.core.config import settings
        provider_name = settings.LLM_PROVIDER.lower()
        return self.get_provider(provider_name)

    def list_providers(self) -> List[str]:
        return list(self._providers.keys())


# Global registry instance
llm_registry = LLMProviderRegistry()

