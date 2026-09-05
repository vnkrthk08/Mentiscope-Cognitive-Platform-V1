import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any


@dataclass
class PromptAuditRecord:
    prompt_id: str
    prompt_version: str
    rendered_hash: str
    provider_name: str
    model_name: str
    latency_ms: int
    prompt_tokens: int
    completion_tokens: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class PromptAuditManager:
    """Records timestamped audit trails for all rendered LLM prompts and model responses."""

    def __init__(self):
        self._audit_log: List[PromptAuditRecord] = []

    def compute_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    def record_audit(
        self,
        prompt_id: str,
        prompt_version: str,
        rendered_text: str,
        provider_name: str,
        model_name: str,
        latency_ms: int,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> PromptAuditRecord:
        record = PromptAuditRecord(
            prompt_id=prompt_id,
            prompt_version=prompt_version,
            rendered_hash=self.compute_hash(rendered_text),
            provider_name=provider_name,
            model_name=model_name,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
        self._audit_log.append(record)
        return record
