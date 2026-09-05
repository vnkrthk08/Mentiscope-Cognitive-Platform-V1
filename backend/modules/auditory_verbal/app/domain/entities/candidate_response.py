from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import uuid


@dataclass
class CandidateResponse(ABC):
    """Abstract Parent Entity for candidate assessment responses."""

    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    prompt_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.session_id or not self.session_id.strip():
            raise ValueError("CandidateResponse session_id cannot be empty.")
        if not self.prompt_id or not self.prompt_id.strip():
            raise ValueError("CandidateResponse prompt_id cannot be empty.")


@dataclass
class ListeningResponse(CandidateResponse):
    """Derived entity for Listening multiple-choice question responses."""

    selected_option_index: int = 0
    response_time_ms: int = 0

    def __post_init__(self):
        super().__post_init__()
        if self.selected_option_index < 0:
            raise ValueError("ListeningResponse selected_option_index cannot be negative.")
        if self.response_time_ms < 0:
            raise ValueError("ListeningResponse response_time_ms cannot be negative.")


@dataclass
class SpeakingResponse(CandidateResponse):
    """Derived entity for Speaking audio responses."""

    audio_file_url: str = ""
    duration_seconds: float = 0.0
    transcript_text: Optional[str] = None
    acoustic_metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        if not self.audio_file_url or not self.audio_file_url.strip():
            raise ValueError("SpeakingResponse audio_file_url cannot be empty.")
        if self.duration_seconds <= 0:
            raise ValueError("SpeakingResponse duration_seconds must be > 0.")
