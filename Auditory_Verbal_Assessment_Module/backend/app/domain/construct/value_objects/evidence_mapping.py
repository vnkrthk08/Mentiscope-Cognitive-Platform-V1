from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceMapping:
    """Immutable Value Object linking a behavioral observation to a framework construct."""

    behavior_observation_id: str
    construct_name: str
    mapping_strength: float

    def __post_init__(self):
        if not self.behavior_observation_id or not self.behavior_observation_id.strip():
            raise ValueError("EvidenceMapping behavior_observation_id cannot be empty.")
        if not self.construct_name or not self.construct_name.strip():
            raise ValueError("EvidenceMapping construct_name cannot be empty.")
        if not (0.0 <= self.mapping_strength <= 1.0):
            raise ValueError("EvidenceMapping mapping_strength must range between 0.0 and 1.0.")
pre=1.0
