from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from app.domain.media.value_objects.processing_status import ProcessingStatus, can_transition
from app.domain.media.value_objects.storage_location import StorageLocation
from app.domain.media.value_objects.audio_metadata import AudioMetadata
from app.domain.media.value_objects.provenance import ValidationResult, AudioProvenance


@dataclass
class AudioAsset:
    """Aggregate Root representing a single audio recording session uploaded by a candidate."""

    asset_id: str
    session_id: str
    assessment_id: str
    candidate_id: str
    storage_location: StorageLocation
    audio_metadata: Optional[AudioMetadata] = None
    processing_status: ProcessingStatus = ProcessingStatus.UPLOADING
    validation_result: Optional[ValidationResult] = None
    provenance: Optional[AudioProvenance] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.asset_id or not self.asset_id.strip():
            raise ValueError("AudioAsset asset_id cannot be empty.")
        if not self.session_id or not self.session_id.strip():
            raise ValueError("AudioAsset session_id cannot be empty.")
        if not self.assessment_id or not self.assessment_id.strip():
            raise ValueError("AudioAsset assessment_id cannot be empty.")
        if not self.candidate_id or not self.candidate_id.strip():
            raise ValueError("AudioAsset candidate_id cannot be empty.")

    def transition_to(self, target: ProcessingStatus):
        """Enforces aggregate root FSM state transition constraints."""
        if not can_transition(self.processing_status, target):
            raise ValueError(
                f"Invariant violation: Cannot transition AudioAsset status from '{self.processing_status.value}' to '{target.value}'."
            )
        self.processing_status = target
        self.updated_at = datetime.now(timezone.utc)
