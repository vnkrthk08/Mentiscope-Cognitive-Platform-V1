from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
from app.domain.speech.value_objects.provider_result import ProviderResult
from app.domain.speech.value_objects.language import Language
from app.domain.speech.value_objects.confidence_score import ConfidenceScore
from app.domain.speech.value_objects.transcript_metadata import TranscriptMetadata
from app.domain.speech.value_objects.word_timestamp import WordTimestamp
from app.domain.speech.entities.speaker_segment import SpeakerSegment


@dataclass
class Transcript:
    """Aggregate Root representing the final normalized transcript of an audio recording session."""

    transcript_id: str
    asset_id: str
    session_id: str
    assessment_id: str
    candidate_id: str
    provider_result: ProviderResult
    language: Language
    confidence_score: ConfidenceScore
    transcript_metadata: TranscriptMetadata
    transcript_text: str
    word_timestamps: List[WordTimestamp] = field(default_factory=list)
    speaker_segments: List[SpeakerSegment] = field(default_factory=list)
    processing_duration_ms: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.transcript_id or not self.transcript_id.strip():
            raise ValueError("Transcript transcript_id cannot be empty.")
        if not self.asset_id or not self.asset_id.strip():
            raise ValueError("Transcript asset_id cannot be empty.")
        if not self.session_id or not self.session_id.strip():
            raise ValueError("Transcript session_id cannot be empty.")
        if not self.assessment_id or not self.assessment_id.strip():
            raise ValueError("Transcript assessment_id cannot be empty.")
        if not self.candidate_id or not self.candidate_id.strip():
            raise ValueError("Transcript candidate_id cannot be empty.")
        if not self.transcript_text or not self.transcript_text.strip():
            raise ValueError("Transcript transcript_text content cannot be empty.")
