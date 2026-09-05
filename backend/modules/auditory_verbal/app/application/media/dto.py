from typing import Dict, Optional
from pydantic import BaseModel, Field


class UploadUrlRequest(BaseModel):
    session_id: str
    assessment_id: str
    content_type: str = Field(..., description="MIME type e.g. audio/wav")
    expected_file_size: int = Field(..., gt=0, description="Expected file size in bytes")


class UploadUrlResponse(BaseModel):
    asset_id: str
    signed_upload_url: str
    expiration: int = 3600  # seconds
    required_headers: Dict[str, str] = Field(default_factory=dict)
    storage_provider: str


class UploadCompleteRequest(BaseModel):
    asset_id: str
    checksum: str = Field(..., description="SHA-256 checksum of uploaded bytes")
    content_length: int = Field(..., gt=0)
    storage_integrity_identifier: Optional[str] = None  # ETag


class UploadCompleteResponse(BaseModel):
    status: str
    message: str
    validation_passed: bool
    quarantined: bool
