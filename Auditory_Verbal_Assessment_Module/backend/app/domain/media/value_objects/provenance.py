from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ValidationResult:
    """Immutable Value Object storing result of checksum and file integrity validation checks."""

    is_valid: bool
    validation_timestamp: datetime
    failure_reason: Optional[str] = None


@dataclass(frozen=True)
class AudioProvenance:
    """Immutable Value Object tracking origin, publisher version, and security details of ingestion."""

    uploaded_by: str
    upload_method: str
    storage_provider: str
    provider_version: str
    pipeline_version: str
    checksum_algorithm: str
    upload_timestamp: datetime
