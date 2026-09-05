import json
from typing import Dict, Any, Tuple


class LLMResponseNormalizer:
    """Normalizes raw LLM chat responses into unified string contents."""

    @staticmethod
    def normalize(provider_name: str, raw_response: Dict[str, Any]) -> Tuple[str, int, int]:
        provider_name = provider_name.lower()

        if "openai" in provider_name or "openrouter" in provider_name or "mock" in provider_name:
            content = raw_response.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content:
                content = raw_response.get("content", "")
            usage = raw_response.get("usage", {})
            return content, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)

        elif "claude" in provider_name:
            content = raw_response["content"][0]["text"]
            usage = raw_response.get("usage", {})
            return content, usage.get("input_tokens", 0), usage.get("output_tokens", 0)

        elif "gemini" in provider_name:
            if "choices" in raw_response:
                # Real Gemini compatibility response
                content = raw_response["choices"][0]["message"]["content"]
                usage = raw_response.get("usage", {})
                return content, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
            else:
                # Mock response
                content = raw_response["candidates"][0]["content"]["parts"][0]["text"]
                usage = raw_response.get("usageMetadata", {})
                return (
                    content,
                    usage.get("promptTokenCount", 0),
                    usage.get("candidatesTokenCount", 0),
                )

        else:
            raise ValueError(f"No response normalizer mapping found for provider '{provider_name}'.")

