from dataclasses import dataclass


@dataclass
class SpeakerSegment:
    """Domain Entity representing a specific segment of speaker audio (for diarization support)."""

    speaker_id: str
    start_time: float
    end_time: float
    text: str

    def __post_init__(self):
        if not self.speaker_id or not self.speaker_id.strip():
            raise ValueError("SpeakerSegment speaker_id cannot be empty.")
        if self.start_time < 0 or self.end_time < 0 or self.end_time < self.start_time:
            raise ValueError("SpeakerSegment start/end timings must be positive and ordered.")
        if not self.text or not self.text.strip():
            raise ValueError("SpeakerSegment text content cannot be empty.")
