"""ConfigurationProfile Entity."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import hashlib
import json
import uuid


@dataclass
class ConfigurationProfile:
    """Versioned, immutable configuration profile for environment management."""

    profile_name: str  # e.g., "production", "staging", "development"
    created_by: str
    config_data: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    is_active: bool = True
    config_hash: str = field(init=False)
    profile_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = ""

    def __post_init__(self) -> None:
        if not self.profile_name:
            raise ValueError("ConfigurationProfile profile_name cannot be empty.")
        if not self.created_by:
            raise ValueError("ConfigurationProfile created_by cannot be empty.")
        self.config_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        serialized = json.dumps(self.config_data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "profile_name": self.profile_name,
            "created_by": self.created_by,
            "config_data": self.config_data,
            "version": self.version,
            "is_active": self.is_active,
            "config_hash": self.config_hash,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }
