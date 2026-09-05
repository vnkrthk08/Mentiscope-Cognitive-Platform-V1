import json
import uuid
import time
import os
import httpx
from typing import Dict, Any, List
from app.infrastructure.prompt.providers.base_provider import LLMProvider


from app.core.config import settings


class OpenAIProvider(LLMProvider):
    """OpenAI chat generation provider integration."""

    def __init__(self, api_key: str = "", default_model: str = "gpt-4o"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.default_model = settings.OPENAI_MODEL or default_model

    @property
    def provider_name(self) -> str:
        return "openai"

    def health(self) -> bool:
        return True

    async def generate(self, system_prompt: str = None, user_prompt: str = None, prompt_text: str = None, options: Dict[str, Any] = None) -> Dict[str, Any]:
        # Resolve prompt arguments (supporting both LLMProvider and ILLMProvider signatures)
        sys_p = system_prompt
        usr_p = user_prompt
        opts = options or {}

        # Handle generate(prompt_text, options) where options is passed as second positional argument
        if isinstance(user_prompt, dict):
            opts = user_prompt
            usr_p = system_prompt
            sys_p = "You are a helpful assistant."
        elif system_prompt is not None and user_prompt is None and isinstance(system_prompt, str):
            sys_p = "You are a helpful assistant."
            usr_p = system_prompt
            if isinstance(prompt_text, dict):
                opts = prompt_text
        elif prompt_text is not None:
            usr_p = prompt_text
            sys_p = system_prompt or "You are a helpful assistant."
            if isinstance(options, dict):
                opts = options

        if settings.LLM_MODE != "real":
            # Support prompt-aware mock fallback in case provider is invoked in mock mode
            prompt_id = opts.get("prompt_id", "UNKNOWN")
            if "follow_up" in prompt_id.lower() or "adaptive" in prompt_id.lower():
                mock_analysis = {
                    "internal_reasoning": "The candidate provided a structured approach. I should challenge them on how they will handle conflict.",
                    "answer_quality": "GOOD",
                    "intent": "Prioritizing structural conflict resolution",
                    "is_relevant": True,
                    "needs_clarification": False,
                    "follow_up_question": "That's an interesting approach. Suppose one of your teammates disagrees with your plan. What would you do next?",
                    "behavioral_evidence": [
                        {
                            "category": "Decision Making",
                            "quote": "Our team must prioritize safety protocols",
                            "confidence": 0.94
                        }
                    ]
                }
            elif "construct" in prompt_id.lower() or "evaluation" in prompt_id.lower():
                mock_analysis = {
                    "construct_evaluations": [
                        {
                            "construct": "DECISION_MAKING",
                            "behavioral_summary": "Communicates decision rationale systematically under pressure.",
                            "evaluation_narrative": "Multiple evidence items consistently demonstrate ethical prioritization and structured problem-solving.",
                            "confidence": 0.95,
                        }
                    ]
                }
            else:
                mock_analysis = {
                    "behaviors": [
                        {
                            "category": "Leadership",
                            "description": "Candidate demonstrates ownership by greeting and introducing the task.",
                            "quote": "Hello, welcome to MentiScope assessment engine.",
                            "start_word_index": 0,
                            "end_word_index": 5,
                            "start_time": 0.0,
                            "end_time": 5.2,
                            "confidence": 0.98,
                            "linked_constructs": ["Leadership", "Communication"],
                        }
                    ]
                }
            content_str = json.dumps(mock_analysis)
            # Support APOS & traditional response formats
            return {
                "choices": [
                    {
                        "message": {
                            "content": content_str,
                            "role": "assistant",
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": 450,
                    "completion_tokens": 120,
                    "total_tokens": 570,
                },
                "id": f"chatcmpl-{uuid.uuid4()}",
                "model": self.default_model,
                "latency_ms": 250.0,

                # APOS style
                "content": content_str,
                "raw_payload": mock_analysis,
                "provider": "openai",
                "prompt_tokens": 450,
                "completion_tokens": 120,
                "total_tokens": 570,
            }

        # Real mode
        api_key = self.api_key or settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        model = settings.OPENAI_MODEL or self.default_model

        temp = opts.get("temperature", 0.7)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": sys_p},
                {"role": "user", "content": usr_p}
            ],
            "temperature": temp,
            "response_format": {"type": "json_object"}
        }

        start_time = time.time()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            raw_data = response.json()
        latency_ms = (time.time() - start_time) * 1000

        choices = raw_data.get("choices", [])
        if not choices:
            raise ValueError(f"OpenAI returned empty choices: {raw_data}")

        usage = raw_data.get("usage", {})
        input_tok = usage.get("prompt_tokens", 0)
        output_tok = usage.get("completion_tokens", 0)
        content_str = choices[0]["message"]["content"]

        try:
            raw_payload = json.loads(content_str)
        except Exception:
            raw_payload = content_str

        return {
            "choices": choices,
            "usage": usage,
            "id": raw_data.get("id", f"chatcmpl-{uuid.uuid4()}"),
            "model": model,
            "latency_ms": latency_ms,

            # APOS support
            "content": content_str,
            "raw_payload": raw_payload,
            "provider": "openai",
            "prompt_tokens": input_tok,
            "completion_tokens": output_tok,
            "total_tokens": input_tok + output_tok,
        }

    async def health_check(self) -> bool:
        api_key = self.api_key or settings.OPENAI_API_KEY
        if not api_key:
            return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {api_key}"}, timeout=5.0)
                return resp.status_code == 200
        except Exception:
            return False

    def supported_models(self) -> List[str]:
        return ["gpt-4o", "gpt-4", "gpt-3.5-turbo"]

    def max_context_window(self, model_name: str) -> int:
        return 128000

    def estimate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        # GPT-4o pricing: $0.005 / 1K input, $0.015 / 1K output
        input_cost = (input_tokens / 1000.0) * 0.005
        output_cost = (output_tokens / 1000.0) * 0.015
        return round(input_cost + output_cost, 6)

