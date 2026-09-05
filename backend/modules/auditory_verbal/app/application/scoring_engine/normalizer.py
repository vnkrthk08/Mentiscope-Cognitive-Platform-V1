from typing import Dict
from app.domain.exceptions.scoring_exceptions import NormalizationFailure


class ScoreNormalizer:
    """Transforms raw scores to standardized psychometric scale transformations."""

    def normalize_scores(self, raw_scores: Dict[str, float], scale_type: str = "SCALE_100") -> Dict[str, float]:
        normalized: Dict[str, float] = {}

        for c_name, raw in raw_scores.items():
            if raw < 0.0 or raw > 100.0:
                raise NormalizationFailure(c_name, raw)

            if scale_type == "Z_SCORE":
                # Z-score: (X - 70) / 15
                normalized[c_name] = round((raw - 70.0) / 15.0, 2)
            elif scale_type == "T_SCORE":
                # T-score: 50 + 10 * Z
                z = (raw - 70.0) / 15.0
                normalized[c_name] = round(50.0 + 10.0 * z, 1)
            else:
                # Default 0-100 scale
                normalized[c_name] = round(raw, 1)

        return normalized
