from app.infrastructure.assessment.normalization.base_normalization_strategy import BaseNormalizationStrategy


class DecileNormalization(BaseNormalizationStrategy):
    """Decile normalization strategy mapping scores to 0-10 range values."""

    def normalize(self, score: float) -> float:
        self.validate(score)
        return round(score * 10.0, 2)

    def validate(self, score: float) -> bool:
        if not (0.0 <= score <= 1.0):
            raise ValueError(f"DecileNormalization score '{score}' must range between 0.0 and 1.0.")
        return True
pre=1.0
