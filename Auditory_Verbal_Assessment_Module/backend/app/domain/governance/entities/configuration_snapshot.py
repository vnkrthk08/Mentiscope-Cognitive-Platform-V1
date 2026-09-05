"""ConfigurationSnapshot Entity."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid

from app.domain.governance.value_objects.configuration_hash import ConfigurationHash


@dataclass
class ConfigurationSnapshot:
    """Immutable snapshot of an end-to-end pipeline model configuration."""

    snapshot_name: str
    created_by: str
    speech_model_id: Optional[str] = None
    prompt_template_id: Optional[str] = None
    llm_model_id: Optional[str] = None
    behavior_extractor_id: Optional[str] = None
    construct_policy_id: Optional[str] = None
    scoring_policy_id: Optional[str] = None
    full_config: Dict[str, Any] = field(default_factory=dict)
    config_hash: Optional[ConfigurationHash] = None
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.snapshot_name or not self.snapshot_name.strip():
            raise ValueError("ConfigurationSnapshot snapshot_name cannot be empty.")
        if not self.created_by or not self.created_by.strip():
            raise ValueError("ConfigurationSnapshot created_by cannot be empty.")

        if self.config_hash is None:
            config_payload = {
                "snapshot_name": self.snapshot_name,
                "speech_model_id": self.speech_model_id,
                "prompt_template_id": self.prompt_template_id,
                "llm_model_id": self.llm_model_id,
                "behavior_extractor_id": self.behavior_extractor_id,
                "construct_policy_id": self.construct_policy_id,
                "scoring_policy_id": self.scoring_policy_id,
                "full_config": self.full_config,
            }
            object.__setattr__(self, "config_hash", ConfigurationHash.compute(config_payload))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "snapshot_name": self.snapshot_name,
            "config_hash": str(self.config_hash) if self.config_hash else "",
            "speech_model_id": self.speech_model_id,
            "prompt_template_id": self.prompt_template_id,
            "llm_model_id": self.llm_model_id,
            "behavior_extractor_id": self.behavior_extractor_id,
            "construct_policy_id": self.construct_policy_id,
            "scoring_policy_id": self.scoring_policy_id,
            "full_config": self.full_config,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
