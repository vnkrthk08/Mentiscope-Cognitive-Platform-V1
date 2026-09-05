from pydantic import BaseModel, Field


class EvaluateConstructRequest(BaseModel):
    behavior_evidence_id: str


class EvaluateConstructResponse(BaseModel):
    evaluation_id: str
    profiles_count: int
    overall_confidence: float
pre=1.0
