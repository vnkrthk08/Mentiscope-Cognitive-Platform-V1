"""ConfigurationHash Value Object."""
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Dict


@dataclass(frozen=True)
class ConfigurationHash:
    """SHA-256 integrity hash tag for configuration snapshots."""

    value: str

    @classmethod
    def compute(cls, config_data: Dict[str, Any]) -> "ConfigurationHash":
        serialized = json.dumps(config_data, sort_keys=True, default=str)
        sha = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return cls(value=sha)

    def __str__(self) -> str:
        return self.value
