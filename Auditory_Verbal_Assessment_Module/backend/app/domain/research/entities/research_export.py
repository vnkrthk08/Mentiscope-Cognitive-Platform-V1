"""
ResearchExport Entity.

Represents a completed export job — tracking which datasets were
included, the format used, the storage location, and checksum.
Supports CSV, JSON, and Excel formats.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class ResearchExport:
    """
    Entity tracking a research dataset export job.

    Each export is immutable once finalised.
    Exports preserve full traceability references.
    """

    # Identity
    export_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    export_name: str = ""

    # Contents
    dataset_ids: List[str] = field(default_factory=list)
    calibration_batch_id: Optional[str] = None
    record_count: int = 0

    # Format
    export_format: str = "CSV"   # CSV | JSON | EXCEL
    include_evidence: bool = True
    include_transcripts: bool = True
    include_expert_reviews: bool = True
    include_construct_mappings: bool = True

    # Storage
    file_path: Optional[str] = None
    file_size_bytes: int = 0
    checksum_sha256: Optional[str] = None

    # Metadata
    requested_by: str = ""
    export_metadata: Dict[str, Any] = field(default_factory=dict)

    # Lifecycle
    status: str = "PENDING"   # PENDING | IN_PROGRESS | COMPLETED | FAILED
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    # ---------------------------------------------------------------------------
    # Business rules
    # ---------------------------------------------------------------------------

    def mark_in_progress(self) -> None:
        if self.status != "PENDING":
            raise ValueError(f"Export must be PENDING to start, not '{self.status}'.")
        self.status = "IN_PROGRESS"

    def mark_completed(
        self,
        file_path: str,
        file_size_bytes: int,
        record_count: int,
        checksum: Optional[str] = None,
    ) -> None:
        if self.status != "IN_PROGRESS":
            raise ValueError("Export must be IN_PROGRESS to complete.")
        self.file_path = file_path
        self.file_size_bytes = file_size_bytes
        self.record_count = record_count
        self.checksum_sha256 = checksum
        self.status = "COMPLETED"
        self.completed_at = datetime.now(timezone.utc)

    def mark_failed(self, reason: str) -> None:
        self.status = "FAILED"
        self.error_message = reason
        self.completed_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "export_id": self.export_id,
            "export_name": self.export_name,
            "dataset_ids": self.dataset_ids,
            "calibration_batch_id": self.calibration_batch_id,
            "record_count": self.record_count,
            "export_format": self.export_format,
            "include_evidence": self.include_evidence,
            "include_transcripts": self.include_transcripts,
            "include_expert_reviews": self.include_expert_reviews,
            "include_construct_mappings": self.include_construct_mappings,
            "file_path": self.file_path,
            "file_size_bytes": self.file_size_bytes,
            "checksum_sha256": self.checksum_sha256,
            "requested_by": self.requested_by,
            "export_metadata": self.export_metadata,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
