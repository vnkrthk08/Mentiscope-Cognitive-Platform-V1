import re
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from app.application.speech.fluency_config import FluencyConfig, DEFAULT_FLUENCY_CONFIG
from app.core.logging import logger


class FluencySource(str, Enum):
    AUDIO_ACOUSTIC = "AUDIO_ACOUSTIC"       # Scenario A: Full audio & transcript available
    TEXT_ONLY = "TEXT_ONLY"                 # Scenario B: Transcript only, no audio
    PARTIAL_ACOUSTIC = "PARTIAL_ACOUSTIC"   # Scenario C: Rate available, pause missing
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA" # Scenario D: Minimal tokens (<4 words)
    SYSTEM_DEGRADED = "SYSTEM_DEGRADED"     # Scenario E: System fault / corrupted payload


@dataclass(frozen=True)
class FluencyResult:
    """Immutable result of fluency delivery evaluation with explicit provenance."""
    score: float                        # 0.0 to 100.0
    fluency_source: FluencySource
    error_flag: bool = False
    rate_score: float = 0.0
    pause_score: float = 0.0
    coherence_score: float = 0.0
    words_per_minute: float = 0.0
    words_per_second: float = 0.0
    pause_ratio: float = 0.0
    word_count: int = 0
    filler_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class FluencyEngine:
    """Evaluates oral delivery characteristics (pace, articulation, lexical continuity).
    Guarantees non-blocking graceful degradation across Scenarios A through E.
    Zero arbitrary fallbacks: technical failures never award unearned student credit.
    """

    FILLER_WORDS = {
        "um", "uh", "er", "ah", "like", "you know", "i mean", "sort of", "kind of",
        "maybe", "guess", "dunno"
    }

    def __init__(self, config: Optional[FluencyConfig] = None):
        self.config = config or DEFAULT_FLUENCY_CONFIG

    def evaluate(
        self,
        transcript_text: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        audio_file_url: Optional[str] = None,
        words_per_second: Optional[float] = None,
        pause_ratio: Optional[float] = None,
    ) -> FluencyResult:
        """Main entry point for delivery evaluation with strict scenario resolution."""
        try:
            clean_text = (transcript_text or "").strip()
            words = clean_text.split() if clean_text else []
            word_count = len(words)

            # Scenario E / Zero Silence: Completely empty response
            if word_count == 0:
                return FluencyResult(
                    score=0.0,
                    fluency_source=FluencySource.INSUFFICIENT_DATA if transcript_text is not None else FluencySource.SYSTEM_DEGRADED,
                    error_flag=False,
                    word_count=0,
                    metadata={"reason": "Empty or absent transcript"},
                )

            # Scenario D: Insufficient Data (<4 words)
            if word_count < 4:
                # Grounded strictly in observable token volume: word_count * 5.0
                insufficient_score = round(word_count * 5.0, 1)
                return FluencyResult(
                    score=insufficient_score,
                    fluency_source=FluencySource.INSUFFICIENT_DATA,
                    error_flag=False,
                    coherence_score=insufficient_score,
                    word_count=word_count,
                    metadata={"reason": f"Minimal response ({word_count} words)"},
                )

            # Count fillers
            lower_text = clean_text.lower()
            filler_count = 0
            for filler in self.FILLER_WORDS:
                filler_count += len(re.findall(r"\b" + re.escape(filler) + r"\b", lower_text))

            # Compute Coherence Score (S_coherence)
            coherence_score = self._compute_coherence_score(word_count, filler_count)

            has_valid_audio = (
                bool(audio_file_url)
                and duration_seconds is not None
                and duration_seconds >= 2.0
            )

            # Scenario B: Transcript Only (No audio metadata or recording)
            if not has_valid_audio:
                return FluencyResult(
                    score=round(coherence_score, 1),
                    fluency_source=FluencySource.TEXT_ONLY,
                    error_flag=False,
                    coherence_score=coherence_score,
                    word_count=word_count,
                    filler_count=filler_count,
                    metadata={"reason": "Audio metadata unavailable; evaluated from transcript coherence"},
                )

            # Valid duration exists -> Compute WPM and Rate Score
            dur = max(0.1, duration_seconds)
            wpm = (word_count / dur) * 60.0
            wps = words_per_second if words_per_second is not None else (word_count / dur)
            rate_score = self._compute_rate_score(wpm)

            # Check if pause ratio is available
            if pause_ratio is not None and 0.0 <= pause_ratio <= 1.0:
                # Scenario A: Full Acoustic & Transcript Available
                pause_score = self._compute_pause_score(pause_ratio)
                composite = (
                    self.config.weight_rate * rate_score
                    + self.config.weight_pause * pause_score
                    + self.config.weight_coherence * coherence_score
                )
                final_score = round(min(100.0, max(0.0, composite)), 1)

                return FluencyResult(
                    score=final_score,
                    fluency_source=FluencySource.AUDIO_ACOUSTIC,
                    error_flag=False,
                    rate_score=rate_score,
                    pause_score=pause_score,
                    coherence_score=coherence_score,
                    words_per_minute=round(wpm, 1),
                    words_per_second=round(wps, 2),
                    pause_ratio=round(pause_ratio, 3),
                    word_count=word_count,
                    filler_count=filler_count,
                )
            else:
                # Scenario C: Partial Acoustic Metrics (Rate available, pause missing)
                # Re-weight available components: 0.40 Rate + 0.25 Coherence = 0.65
                avail_weights = self.config.weight_rate + self.config.weight_coherence
                composite = (
                    (self.config.weight_rate * rate_score + self.config.weight_coherence * coherence_score)
                    / avail_weights
                )
                final_score = round(min(100.0, max(0.0, composite)), 1)

                return FluencyResult(
                    score=final_score,
                    fluency_source=FluencySource.PARTIAL_ACOUSTIC,
                    error_flag=False,
                    rate_score=rate_score,
                    pause_score=100.0,  # Unmeasured pause does not penalize
                    coherence_score=coherence_score,
                    words_per_minute=round(wpm, 1),
                    words_per_second=round(wps, 2),
                    pause_ratio=0.0,
                    word_count=word_count,
                    filler_count=filler_count,
                    metadata={"reason": "Pause segmentation unavailable; re-weighted rate and coherence"},
                )

        except Exception as e:
            # Scenario E: Complete System Fault
            logger.error(f"[FLUENCY ENGINE] Subsystem error during evaluation: {e}", exc_info=True)
            return FluencyResult(
                score=0.0,
                fluency_source=FluencySource.SYSTEM_DEGRADED,
                error_flag=True,
                metadata={"error": str(e)},
            )

    def _compute_rate_score(self, wpm: float) -> float:
        """Piecewise linear rate score honoring the broad 80-180 WPM optimal window."""
        if self.config.min_wpm_optimal <= wpm <= self.config.max_wpm_optimal:
            return 100.0
        elif wpm < self.config.min_wpm_optimal:
            # Below 80 WPM: gentle slope down to 0 at severe_low_wpm (50 WPM)
            gap = self.config.min_wpm_optimal - wpm
            span = max(1.0, self.config.min_wpm_optimal - self.config.severe_low_wpm)
            return max(0.0, 100.0 - (gap / span) * 100.0)
        else:
            # Above 180 WPM: gentle slope down to 0 at severe_high_wpm (220 WPM)
            gap = wpm - self.config.max_wpm_optimal
            span = max(1.0, self.config.severe_high_wpm - self.config.max_wpm_optimal)
            return max(0.0, 100.0 - (gap / span) * 100.0)

    def _compute_pause_score(self, pause_ratio: float) -> float:
        """Evaluates pause ratio allowing natural deliberation (<= 40% silence)."""
        if self.config.min_pause_ratio_optimal <= pause_ratio <= self.config.max_pause_ratio_optimal:
            return 100.0
        elif pause_ratio > self.config.max_pause_ratio_optimal:
            # Silence exceeds 40%: penalize excess pauses
            excess = pause_ratio - self.config.max_pause_ratio_optimal
            return max(0.0, 100.0 - (excess * 200.0))
        else:
            # Below 10%: unnaturally rushed
            deficit = self.config.min_pause_ratio_optimal - pause_ratio
            return max(50.0, 100.0 - (deficit * 200.0))

    def _compute_coherence_score(self, word_count: int, filler_count: int) -> float:
        """Evaluates lexical volume and discourse continuity from transcript."""
        filler_ratio = filler_count / max(1, word_count)
        if word_count >= self.config.min_coherent_words:
            if filler_ratio <= 0.10:
                return 100.0
            elif filler_ratio <= 0.20:
                return 80.0
            else:
                return 65.0
        elif word_count >= 15:
            return 75.0
        elif word_count >= 8:
            return 50.0
        elif word_count >= 4:
            return 25.0
        else:
            return round(word_count * 5.0, 1)
