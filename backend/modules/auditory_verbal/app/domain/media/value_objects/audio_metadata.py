from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AudioMetadata:
    """Immutable Value Object storing raw technical parameters of uploaded audio assets."""

    content_type: str
    duration_seconds: float
    sample_rate: int
    channels: int
    bit_depth: int
    codec: str
    file_size_bytes: int
    checksum_sha256: str

    def __post_init__(self):
        if self.duration_seconds < 0:
            raise ValueError("AudioMetadata duration_seconds must be positive.")
        if self.sample_rate <= 0:
            raise ValueError("AudioMetadata sample_rate must be positive.")
        if self.channels <= 0:
            raise ValueError("AudioMetadata channels must be positive.")
        if self.bit_depth <= 0:
            raise ValueError("AudioMetadata bit_depth must be positive.")
        if not self.checksum_sha256 or not self.checksum_sha256.strip():
            raise ValueError("AudioMetadata checksum_sha256 cannot be empty.")
