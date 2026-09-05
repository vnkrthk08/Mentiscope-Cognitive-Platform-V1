from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import uuid


@dataclass(frozen=True)
class WordTimestamp:
    word: str
    start_time: float
    end_time: float
    confidence: float


@dataclass(frozen=True)
class TranscriptSegment:
    segment_id: int
    start_time: float
    end_time: float
    text: str
    confidence: float


@dataclass(frozen=True)
class Transcript:
    full_text: str
    segments: List[TranscriptSegment]
    word_timestamps: List[WordTimestamp]
    language: str = "en-US"
    version: str = "1.0.0"


@dataclass(frozen=True)
class SpeechProcessingMetadata:
    provider_name: str
    provider_version: str
    model_version: str
    processing_duration_seconds: float
    overall_confidence: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class SpeechProcessingResult:
    """Immutable result payload produced exclusively by Speech Processing Service."""

    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    prompt_id: str = ""
    audio_url: str = ""
    transcript: Transcript = field(default_factory=lambda: Transcript("", [], []))
    metadata: SpeechProcessingMetadata = field(
        default_factory=lambda: SpeechProcessingMetadata("MockProvider", "1.0", "mock-v1", 0.0, 1.0)
    )
    errors: Optional[List[str]] = None


class TranscriptBuilder:
    """Constructs standardized immutable SpeechProcessingResult objects from raw provider payloads."""

    def build_result(
        self,
        session_id: str,
        prompt_id: str,
        audio_url: str,
        raw_provider_data: Dict[str, Any],
        processing_duration_sec: float,
    ) -> SpeechProcessingResult:
        full_text = raw_provider_data.get("text", "")
        lang = raw_provider_data.get("language", "en-US")
        overall_conf = raw_provider_data.get("overall_confidence", 0.95)

        # Build WordTimestamps
        words: List[WordTimestamp] = []
        for w in raw_provider_data.get("word_timestamps", []):
            wt = WordTimestamp(
                word=w["word"],
                start_time=float(w["start_time"]),
                end_time=float(w["end_time"]),
                confidence=float(w["confidence"]),
            )
            words.append(wt)

        # Build TranscriptSegments
        segments: List[TranscriptSegment] = []
        for s in raw_provider_data.get("segments", []):
            seg = TranscriptSegment(
                segment_id=int(s.get("id", 0)),
                start_time=float(s["start"]),
                end_time=float(s["end"]),
                text=s["text"],
                confidence=float(s.get("confidence", 0.95)),
            )
            segments.append(seg)

        transcript = Transcript(
            full_text=full_text,
            segments=segments,
            word_timestamps=words,
            language=lang,
        )

        metadata = SpeechProcessingMetadata(
            provider_name=raw_provider_data.get("provider_name", "MockProvider"),
            provider_version=raw_provider_data.get("provider_version", "1.0.0"),
            model_version=raw_provider_data.get("model_version", "mock-model"),
            processing_duration_seconds=round(processing_duration_sec, 3),
            overall_confidence=overall_conf,
        )

        return SpeechProcessingResult(
            session_id=session_id,
            prompt_id=prompt_id,
            audio_url=audio_url,
            transcript=transcript,
            metadata=metadata,
        )
