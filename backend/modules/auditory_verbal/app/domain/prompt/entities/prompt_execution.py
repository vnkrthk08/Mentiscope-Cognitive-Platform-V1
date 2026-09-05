from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from app.domain.prompt.value_objects.provider_result import ProviderResult
from app.domain.prompt.value_objects.token_usage import TokenUsage
from app.domain.prompt.value_objects.prompt_metadata import PromptMetadata
from app.domain.prompt.entities.prompt_response import PromptResponse


@dataclass
class PromptExecution:
    """Aggregate Root representing a single AI LLM prompt processing pipeline execution."""

    execution_id: str
    transcript_id: str
    prompt_template: str
    prompt_version: str
    assembled_context: str
    provider_result: Optional[ProviderResult] = None
    response: Optional[PromptResponse] = None
    token_usage: Optional[TokenUsage] = None
    execution_metadata: Optional[PromptMetadata] = None
    status: str = "PENDING"  # PENDING, EXECUTING, COMPLETED, FAILED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if not self.execution_id or not self.execution_id.strip():
            raise ValueError("PromptExecution execution_id cannot be empty.")
        if not self.transcript_id or not self.transcript_id.strip():
            raise ValueError("PromptExecution transcript_id cannot be empty.")
        if not self.prompt_template or not self.prompt_template.strip():
            raise ValueError("PromptExecution prompt_template cannot be empty.")
        if self.status not in {"PENDING", "EXECUTING", "COMPLETED", "FAILED"}:
            raise ValueError(f"PromptExecution status '{self.status}' is invalid.")

    def start(self):
        self.status = "EXECUTING"

    def complete(self, result: ProviderResult, response: PromptResponse, usage: TokenUsage, meta: PromptMetadata):
        self.status = "COMPLETED"
        self.provider_result = result
        self.response = response
        self.token_usage = usage
        self.execution_metadata = meta
        self.completed_at = datetime.now(timezone.utc)

    def fail(self):
        self.status = "FAILED"
        self.completed_at = datetime.now(timezone.utc)
