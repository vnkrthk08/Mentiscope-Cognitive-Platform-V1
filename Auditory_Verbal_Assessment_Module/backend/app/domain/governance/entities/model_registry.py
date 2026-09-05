"""RegisteredModel Entity — Governance Model Registry."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid

from app.domain.governance.value_objects.model_version import ModelVersion


@dataclass
class RegisteredModel:
    """Registered AI model or pipeline component in the governance registry."""

    name: str
    category: str  # SPEECH, PROMPT_TEMPLATE, LLM_MODEL, BEHAVIOR_EXTRACTOR, CONSTRUCT_MAPPING, SCORING_POLICY
    version: ModelVersion
    owner: str
    description: str = ""
    checksum: str = ""
    configuration: Dict[str, Any] = field(default_factory=dict)
    status: str = "ACTIVE"  # DRAFT, ACTIVE, DEPRECATED, ARCHIVED
    model_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("RegisteredModel name cannot be empty.")
        if not self.category or not self.category.strip():
            raise ValueError("RegisteredModel category cannot be empty.")
        if not self.owner or not self.owner.strip():
            raise ValueError("RegisteredModel owner cannot be empty.")

    def deprecate(self) -> None:
        if self.status == "ARCHIVED":
            raise ValueError("Cannot deprecate an archived model.")
        self.status = "DEPRECATED"
        self.updated_at = datetime.now(timezone.utc)

    def archive(self) -> None:
        self.status = "ARCHIVED"
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "name": self.name,
            "category": self.category,
            "version": str(self.version),
            "owner": self.owner,
            "description": self.description,
            "checksum": self.checksum,
            "configuration": self.configuration,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
