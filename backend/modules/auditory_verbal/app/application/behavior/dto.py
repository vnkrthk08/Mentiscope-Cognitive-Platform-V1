from pydantic import BaseModel, Field


class ExtractEvidenceRequest(BaseModel):
    prompt_execution_id: str


class ExtractEvidenceResponse(BaseModel):
    evidence_id: str
    validation_passed: bool
    observations_count: int
