from pydantic import BaseModel, Field


class TranscribeRequest(BaseModel):
    asset_id: str
    selection_policy: str = Field("DEFAULT", description="LLM selection strategy")


class TranscribeResponse(BaseModel):
    job_id: str
    status: str = "COMPLETED"
