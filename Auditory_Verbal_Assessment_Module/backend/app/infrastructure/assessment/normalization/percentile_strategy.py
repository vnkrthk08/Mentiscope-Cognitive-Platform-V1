from app.infrastructure.assessment.normalization.base_normalization_strategy import BaseNormalizationStrategy


class PercentileNormalization(BaseNormalizationStrategy):
    """Percentile normalization strategy modeling comparative percentile ranges."""

    def normalize(self, score: float) -> float:
        self.validate(score)
        # Simple percentile calculation mock mapping
        return round(score * 100.0, 2)

    def validate(self, score: float) -> bool:
        if not (0.0 <= score <= 1.0):
            raise ValueError(f"PercentileNormalization score '{score}' must range between 0.0 and 1.0.")
        return True
pre=1.0
