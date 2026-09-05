"""
ResearchMetadata Value Object.

Captures provenance information for a validation dataset record —
which pipeline version produced it, what model and prompt versions
were used, and when it was generated.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class ResearchMetadata:
    """Immutable provenance tag attached to every ValidationDataset."""

    pipeline_version: str
    model_version: str
    prompt_version: str
    scoring_policy_version: str
    generated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    framework_version: str = "1.0.0"
    environment: str = "production"
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.pipeline_version:
            raise ValueError("ResearchMetadata: pipeline_version is required.")
        if not self.model_version:
            raise ValueError("ResearchMetadata: model_version is required.")
        if not self.prompt_version:
            raise ValueError("ResearchMetadata: prompt_version is required.")
        if not self.scoring_policy_version:
            raise ValueError("ResearchMetadata: scoring_policy_version is required.")

    def to_dict(self) -> dict:
        return {
            "pipeline_version": self.pipeline_version,
            "model_version": self.model_version,
            "prompt_version": self.prompt_version,
            "scoring_policy_version": self.scoring_policy_version,
            "generated_at": self.generated_at.isoformat(),
            "framework_version": self.framework_version,
            "environment": self.environment,
            "notes": self.notes,
        }
