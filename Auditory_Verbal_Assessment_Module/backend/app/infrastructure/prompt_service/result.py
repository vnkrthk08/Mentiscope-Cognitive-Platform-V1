from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import uuid


@dataclass(frozen=True)
class PromptOrchestrationResult:
    """Standardized result payload produced exclusively by AI Prompt Orchestration Service."""

    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    prompt_id: str = ""
    prompt_version: str = "1.0.0"
    rendered_prompt: str = ""
    rendered_hash: str = ""
    selected_provider: str = ""
    selected_model: str = ""
    variables_used: Dict[str, Any] = field(default_factory=dict)
    validated_response: Dict[str, Any] = field(default_factory=dict)
    latency_ms: int = 0
    token_usage: Dict[str, int] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
