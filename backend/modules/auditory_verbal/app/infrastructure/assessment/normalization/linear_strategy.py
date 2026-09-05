from app.infrastructure.assessment.normalization.base_normalization_strategy import BaseNormalizationStrategy


class LinearNormalization(BaseNormalizationStrategy):
    """Linear scaling normalizer mapping scores directly to standard 0-100 range values."""

    def normalize(self, score: float) -> float:
        self.validate(score)
        # Scales 0.0-1.0 score to 0.0-100.0
        return round(score * 100.0, 4)

    def validate(self, score: float) -> bool:
        if not (0.0 <= score <= 1.0):
            raise ValueError(f"LinearNormalization score '{score}' must range between 0.0 and 1.0.")
        return True
pre=1.0
