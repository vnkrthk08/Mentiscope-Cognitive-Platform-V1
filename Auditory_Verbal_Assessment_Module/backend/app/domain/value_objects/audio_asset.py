from dataclasses import dataclass


@dataclass(frozen=True)
class AudioAsset:
    """Immutable Value Object representing an audio asset media file."""

    url: str
    duration_seconds: float
    format: str = "audio/mp3"

    def __post_init__(self):
        if not self.url or not self.url.strip():
            raise ValueError("Audio asset URL cannot be empty.")
        if self.duration_seconds <= 0:
            raise ValueError("Audio asset duration must be greater than 0 seconds.")
