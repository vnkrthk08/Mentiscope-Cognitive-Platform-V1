import json
import uuid
import time
import os
import httpx
from typing import Dict, Any, List
from app.infrastructure.prompt.providers.base_provider import LLMProvider


from app.core.config import settings


class ClaudeProvider(LLMProvider):
    """Anthropic Claude chat generation provider integration."""

    def __init__(self, api_key: str = "", default_model: str = "claude-3-5-sonnet"):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.default_model = settings.CLAUDE_MODEL or default_model

    @property
    def provider_name(self) -> str:
        return "claude"

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
                "content": [
                    {
                        "text": content_str,
                        "type": "text",
                    }
                ],
                "usage": {
                    "input_tokens": 520,
                    "output_tokens": 150,
                },
                "id": f"msg_{uuid.uuid4()}",
                "model": self.default_model,
                "latency_ms": 310.0,

                # APOS style
                "raw_payload": mock_analysis,
                "provider": "claude",
                "prompt_tokens": 520,
                "completion_tokens": 150,
                "total_tokens": 670,
            }

        # Real mode
        api_key = self.api_key or settings.ANTHROPIC_API_KEY
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured.")

        model = settings.CLAUDE_MODEL or self.default_model

        temp = opts.get("temperature", 0.7)

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": model,
            "max_tokens": 4096,
            "system": sys_p,
            "messages": [
                {"role": "user", "content": usr_p}
            ],
            "temperature": temp,
        }

        start_time = time.time()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            raw_data = response.json()
        latency_ms = (time.time() - start_time) * 1000

        content_list = raw_data.get("content", [])
        if not content_list:
            raise ValueError(f"Claude returned empty content: {raw_data}")

        content_str = content_list[0].get("text", "")
        usage = raw_data.get("usage", {})
        input_tok = usage.get("input_tokens", 0)
        output_tok = usage.get("output_tokens", 0)

        try:
            raw_payload = json.loads(content_str)
        except Exception:
            raw_payload = content_str

        return {
            "content": content_list,
            "usage": usage,
            "id": raw_data.get("id", f"msg_{uuid.uuid4()}"),
            "model": model,
            "latency_ms": latency_ms,

            # APOS support
            "raw_payload": raw_payload,
            "provider": "claude",
            "prompt_tokens": input_tok,
            "completion_tokens": output_tok,
            "total_tokens": input_tok + output_tok,
        }

    async def health_check(self) -> bool:
        api_key = self.api_key or settings.ANTHROPIC_API_KEY
        if not api_key:
            return False
        try:
            # Send a tiny/minimal message payload to check health
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            payload = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "ping"}],
            }
            async with httpx.AsyncClient() as client:
                resp = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=5.0)
                return resp.status_code == 200
        except Exception:
            return False

    def supported_models(self) -> List[str]:
        return ["claude-3-5-sonnet", "claude-3-opus", "claude-3-haiku-20240307"]

    def max_context_window(self, model_name: str) -> int:
        return 200000

    def estimate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        # Claude-3-5 pricing: $0.003 / 1K input, $0.015 / 1K output
        input_cost = (input_tokens / 1000.0) * 0.003
        output_cost = (output_tokens / 1000.0) * 0.015
        return round(input_cost + output_cost, 6)

