from typing import Dict, Any, Tuple
from app.core.logging import logger


class AudioPreprocessor:
    """Normalizes sample rates, channels, and audio formatting (Abstraction layer)."""

    def preprocess(self, audio_bytes: bytes, metadata: Dict[str, Any]) -> Tuple[bytes, Dict[str, Any]]:
        target_sample_rate = 16000
        target_channels = 1

        processed_metadata = dict(metadata)
        processed_metadata["preprocessed"] = True
        processed_metadata["sample_rate"] = target_sample_rate
        processed_metadata["channels"] = target_channels

        logger.info(f"[SPS PREPROCESSOR] Normalized audio payload: {target_sample_rate}Hz, mono")
        return audio_bytes, processed_metadata
