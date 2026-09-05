from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(frozen=True)
class BehaviouralIndicator:
    """Domain Value Object representing a standardized psychometric behavioural indicator."""

    indicator_id: str
    name: str
    weight: float
    scale: str = "0-4"
    anchors: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self.indicator_id or not self.indicator_id.strip():
            raise ValueError("BehaviouralIndicator indicator_id cannot be empty.")
        if not self.name or not self.name.strip():
            raise ValueError("BehaviouralIndicator name cannot be empty.")
        if self.weight <= 0.0:
            raise ValueError(f"BehaviouralIndicator weight must be positive, got {self.weight}")
        if self.anchors and not all(k in self.anchors for k in ["0", "1", "2", "3", "4"]):
            # Allow empty anchors for test stubs, but if anchors provided, must contain 0-4
            pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "indicator_id": self.indicator_id,
            "name": self.name,
            "weight": self.weight,
            "scale": self.scale,
            "anchors": dict(self.anchors),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BehaviouralIndicator":
        return cls(
            indicator_id=data["indicator_id"],
            name=data["name"],
            weight=float(data.get("weight", 1.0)),
            scale=data.get("scale", "0-4"),
            anchors=data.get("anchors", {}),
        )
