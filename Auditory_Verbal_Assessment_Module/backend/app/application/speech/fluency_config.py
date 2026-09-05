from dataclasses import dataclass


@dataclass(frozen=True)
class FluencyConfig:
    """Configurable psychometric and acoustic thresholds for speech delivery evaluation.
    Encapsulates all Category B and C assumptions to eliminate magic numbers.
    """
    min_wpm_optimal: float = 80.0
    max_wpm_optimal: float = 180.0
    severe_low_wpm: float = 50.0
    severe_high_wpm: float = 220.0
    max_pause_ratio_optimal: float = 0.40
    min_pause_ratio_optimal: float = 0.10
    min_coherent_words: int = 20
    weight_rate: float = 0.40
    weight_pause: float = 0.35
    weight_coherence: float = 0.25


# Global default configuration instance
DEFAULT_FLUENCY_CONFIG = FluencyConfig()
