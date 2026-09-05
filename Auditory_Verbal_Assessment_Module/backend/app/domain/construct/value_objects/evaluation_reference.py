from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationReference:
    """Immutable Value Object storing traceability references (scenarios, prompts, aggregates)."""

    reference_id: str
    reference_type: str

    def __post_init__(self):
        if not self.reference_id or not self.reference_id.strip():
            raise ValueError("EvaluationReference reference_id cannot be empty.")
        if not self.reference_type or not self.reference_type.strip():
            raise ValueError("EvaluationReference reference_type cannot be empty.")
pre=1.0
