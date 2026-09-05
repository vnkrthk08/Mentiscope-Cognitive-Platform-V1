"""ModelVersion Value Object."""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ModelVersion:
    """Semantic model/component version (e.g., 1.0.0, v2.1.0-alpha)."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("ModelVersion cannot be empty.")
        cleaned = self.value.strip()
        if len(cleaned) < 1:
            raise ValueError("ModelVersion cannot be whitespace.")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value
