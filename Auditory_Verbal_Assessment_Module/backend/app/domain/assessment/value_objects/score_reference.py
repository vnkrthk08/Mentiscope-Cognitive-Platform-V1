from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreReference:
    """Immutable Value Object storing traceability details for scores evaluation."""

    construct_evaluation_id: str
    behavior_evidence_id: str
    prompt_execution_id: str
    transcript_id: str

    def __post_init__(self):
        for val in [self.construct_evaluation_id, self.behavior_evidence_id, self.prompt_execution_id, self.transcript_id]:
            if not val or not val.strip():
                raise ValueError("ScoreReference fields cannot be empty.")
pre=1.0
