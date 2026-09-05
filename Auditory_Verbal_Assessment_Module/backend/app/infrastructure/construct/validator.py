from typing import List, Tuple
from app.domain.construct.entities.construct_profile import ConstructProfile


class ConstructValidator:
    """Validates construct evaluation profile segments consistency and frameworks compliance."""

    ALLOWED_FRAMEWORKS = {"CHC", "RIASEC", "PERSONALITY", "EMOTIONAL_REGULATION"}

    @classmethod
    def validate_profiles(cls, profiles: List[ConstructProfile]) -> Tuple[List[ConstructProfile], List[str]]:
        if not profiles:
            return [], ["Evaluation contains no supporting construct profiles."]

        valid = []
        errors = []
        seen = set()

        for p in profiles:
            # 1. Framework validation
            if p.framework.upper() not in cls.ALLOWED_FRAMEWORKS:
                errors.append(f"Framework '{p.framework}' is invalid.")
                continue

            # 2. Duplicate validation
            key = (p.framework.upper(), p.construct_name.lower())
            if key in seen:
                errors.append(f"Duplicate profile mapped for framework '{p.framework}' construct '{p.construct_name}'.")
                continue
            seen.add(key)

            # 3. Confidence threshold verification
            if p.confidence.confidence_score <= 0.0:
                errors.append(f"Invalid confidence score for construct '{p.construct_name}'.")
                continue

            valid.append(p)

        return valid, errors
pre=1.0
