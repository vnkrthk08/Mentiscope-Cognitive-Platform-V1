from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceReference:
    """Immutable Value Object referencing transcripts or prompt executions logs."""

    reference_id: str
    reference_type: str

    def __post_init__(self):
        if not self.reference_id or not self.reference_id.strip():
            raise ValueError("EvidenceReference reference_id cannot be empty.")
        if not self.reference_type or not self.reference_type.strip():
            raise ValueError("EvidenceReference reference_type cannot be empty.")
        if self.reference_type not in {"TRANSCRIPT", "PROMPT_EXECUTION", "SCENARIO"}:
            raise ValueError(f"EvidenceReference reference_type '{self.reference_type}' is invalid.")
