import json
import uuid
import time
import os
import logging
import httpx
import asyncio
from typing import Dict, Any, List
from app.infrastructure.prompt.providers.base_provider import LLMProvider

from app.core.config import settings

logger = logging.getLogger(__name__)

class OpenRouterProvider(LLMProvider):
    """OpenRouter API chat generation provider integration."""

    def __init__(self, api_key: str = "", default_model: str = "nvidia/nemotron-3-ultra-550b-a55b:free"):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.default_model = settings.OPENROUTER_MODEL or default_model

    @property
    def provider_name(self) -> str:
        return "openrouter"

    def health(self) -> bool:
        return True

    async def health_check(self) -> bool:
        api_key = self.api_key or settings.OPENROUTER_API_KEY
        if not api_key:
            return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("https://openrouter.ai/api/v1/models", timeout=5.0)
                return resp.status_code == 200
        except Exception:
            return False

    def supported_models(self) -> List[str]:
        return [self.default_model, "nvidia/nemotron-3-ultra-550b-a55b:free"]

    def max_context_window(self, model_name: str) -> int:
        return 131072

    def estimate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        if "free" in model_name.lower():
            return 0.0
        # Default estimation
        return round((input_tokens * 0.001 + output_tokens * 0.002) / 1000.0, 6)

    async def generate(self, system_prompt: str = None, user_prompt: str = None, prompt_text: str = None, options: Dict[str, Any] = None) -> Dict[str, Any]:
        # Handle interface differences
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

        # Load API key and model config dynamically
        if settings.LLM_MODE != "real":
            # Support prompt-aware mock fallback in case provider is invoked in mock mode
            prompt_id = opts.get("prompt_id", "UNKNOWN")
            if "follow_up" in prompt_id.lower() or "adaptive" in prompt_id.lower():
                t_text = (opts.get("transcript_text") if isinstance(opts, dict) else "") or p_text
                from app.application.followup_subsystem.dialogue_editor import DialogueEditor
                details = DialogueEditor().extract_details_from_text(t_text)
                detail_str = (" and ".join([d["text"] for d in details[:2]])) if details else "your approach"
                mock_question = f"Regarding {detail_str}, what specific risk were you aiming to avoid?"

                mock_analysis = {
                    "internal_reasoning": "The candidate provided a structured approach. Probing risk awareness next.",
                    "answer_quality": "GOOD",
                    "intent": "ASK_RISK",
                    "is_relevant": True,
                    "needs_clarification": False,
                    "follow_up_question": mock_question,
                    "behavioral_evidence": [
                        {
                            "category": "Decision Making",
                            "quote": detail_str,
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
                            "linked_constructs": ["Leadership"]
                        }
                    ]
                }
            content_str = json.dumps(mock_analysis)
            return {
                "choices": [
                    {
                        "message": {
                            "content": content_str,
                            "role": "assistant"
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "total_tokens": 150,
                },
                "id": f"mock-{uuid.uuid4()}",
                "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
                "latency_ms": 50.0,
                "content": content_str,
                "raw_payload": mock_analysis,
                "provider": self.provider_name,
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            }

        api_key = self.api_key or settings.OPENROUTER_API_KEY
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured.")

        model = settings.OPENROUTER_MODEL or self.default_model

        temp = opts.get("temperature", 0.7)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://mentiscope.com",
            "X-Title": "MentiScope",
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
        max_retries = 3
        last_exc = None
        raw_data = None

        async with httpx.AsyncClient() as client:
            for attempt in range(max_retries):
                try:
                    response = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=180.0
                    )
                    if response.status_code == 429 and attempt < max_retries - 1:
                        await asyncio.sleep(2.0 * (2 ** attempt))
                        continue
                    response.raise_for_status()
                    raw_data = response.json()
                    break
                except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                    last_exc = exc
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2.0 * (2 ** attempt))
                        continue
                    raise exc

        latency_ms = (time.time() - start_time) * 1000

        choices = raw_data.get("choices", [])
        if not choices:
            raise ValueError(f"OpenRouter returned empty choices: {raw_data}")

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
            "usage": {
                "prompt_tokens": input_tok,
                "completion_tokens": output_tok,
                "total_tokens": input_tok + output_tok,
            },
            "id": raw_data.get("id", f"or-{uuid.uuid4()}"),
            "model": model,
            "latency_ms": latency_ms,
            
            # APOS support
            "content": content_str,
            "raw_payload": raw_payload,
            "provider": self.provider_name,
            "prompt_tokens": input_tok,
            "completion_tokens": output_tok,
            "total_tokens": input_tok + output_tok,
        }
