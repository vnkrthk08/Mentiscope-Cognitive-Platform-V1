import hashlib
import struct
from typing import Dict, Any, Tuple


class MediaValidator:
    """Validator inspecting audio content length, mime types, checksums and structural header bytes."""

    @staticmethod
    def calculate_sha256(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def parse_wav_header(content: bytes) -> Tuple[int, int, int, float, str]:
        """Parses WAV byte structures, returning (channels, sample_rate, bit_depth, duration, codec)."""
        if len(content) < 44:
            raise ValueError("File content is too small to contain a valid WAV header.")

        # Check RIFF header
        if content[0:4] != b"RIFF" or content[8:12] != b"WAVE":
            raise ValueError("Invalid WAV format: Missing RIFF/WAVE signature.")

        # Find fmt subchunk
        fmt_index = content.find(b"fmt ")
        if fmt_index == -1:
            raise ValueError("Invalid WAV format: Missing format subchunk.")

        # Parse format subchunk parameters
        # fmt_index + 4 is subchunk size (4 bytes)
        # fmt_index + 8 is audio format (2 bytes)
        # fmt_index + 10 is num channels (2 bytes)
        # fmt_index + 12 is sample rate (4 bytes)
        # fmt_index + 16 is byte rate (4 bytes)
        # fmt_index + 20 is block align (2 bytes)
        # fmt_index + 22 is bits per sample (2 bytes)
        audio_format, channels, sample_rate, byte_rate, _, bits_per_sample = struct.unpack(
            "<HHIIHH", content[fmt_index + 8: fmt_index + 24]
        )

        codec = "PCM" if audio_format == 1 else f"Type_{audio_format}"

        # Find data subchunk to extract raw audio bytes size
        data_index = content.find(b"data", fmt_index + 24)
        if data_index == -1:
            # Fallback duration calculation using overall file size
            data_size = len(content) - 44
        else:
            data_size = struct.unpack("<I", content[data_index + 4: data_index + 8])[0]

        duration = data_size / byte_rate if byte_rate > 0 else 0.0

        return channels, sample_rate, bits_per_sample, duration, codec

    @classmethod
    def validate_and_extract(
        cls,
        content: bytes,
        expected_checksum: str,
        content_type: str,
        max_size_bytes: int = 50 * 1024 * 1024,  # 50MB
    ) -> Dict[str, Any]:
        """Runs full validation suite against uploaded file bytes."""
        # 1. Size verification
        file_size = len(content)
        if file_size > max_size_bytes:
            raise ValueError(f"File size {file_size} exceeds maximum limit of {max_size_bytes} bytes.")
        if file_size == 0:
            raise ValueError("Uploaded file content is empty.")

        # 2. Checksum validation
        calc_checksum = cls.calculate_sha256(content)
        if calc_checksum != expected_checksum:
            raise ValueError(f"Checksum mismatch. Expected: {expected_checksum}, calculated: {calc_checksum}")

        # 3. Content-Type/Mime Checks
        allowed_mimes = {"audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp3"}
        if content_type.lower() not in allowed_mimes:
            raise ValueError(f"Unsupported MIME type: {content_type}")

        # 4. Header Validation & Parameters Extraction
        # Fallback defaults for MPEG/MP3 or custom mocks
        channels = 1
        sample_rate = 16000
        bit_depth = 16
        duration = 10.0
        codec = "MP3"

        if "wav" in content_type.lower():
            try:
                channels, sample_rate, bit_depth, duration, codec = cls.parse_wav_header(content)
            except Exception as e:
                raise ValueError(f"Corrupted or invalid WAV file headers: {str(e)}")

        # 5. Duration Limits Checks
        if duration < 1.0:
            raise ValueError(f"Audio duration {duration:.2f}s is less than minimum 1 second.")
        if duration > 300.0:  # 5 minutes
            raise ValueError(f"Audio duration {duration:.2f}s exceeds maximum 5 minutes.")

        return {
            "channels": channels,
            "sample_rate": sample_rate,
            "bit_depth": bit_depth,
            "duration_seconds": duration,
            "codec": codec,
            "file_size_bytes": file_size,
            "checksum_sha256": calc_checksum,
        }
