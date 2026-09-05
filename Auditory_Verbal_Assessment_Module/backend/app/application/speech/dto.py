from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TranscribeRequest(BaseModel):
    asset_id: str
    selection_policy: str = Field("DEFAULT", description="Selection strategy: DEFAULT, FASTEST, LOWEST_COST, HIGHEST_AVAILABILITY")


class TranscribeResponse(BaseModel):
    job_id: str
    status: str = "PENDING"


class JobStatusResponse(BaseModel):
    job_id: str
    asset_id: str
    provider: str
    status: str
    retry_count: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
