from app.application.evidence_engine.models import BehavioralEvidenceSet
from app.domain.exceptions.evidence_exceptions import EvidenceValidationFailure


class EvidenceValidator:
    """Validates extracted BehavioralEvidenceSet completeness, quote references, and confidence thresholds."""

    def validate_evidence_set(self, evidence_set: BehavioralEvidenceSet, min_confidence: float = 0.5) -> bool:
        if not evidence_set.evidence_items:
            raise EvidenceValidationFailure("SET", "BehavioralEvidenceSet contains no evidence items.")

        for item in evidence_set.evidence_items:
            if item.confidence < min_confidence:
                raise EvidenceValidationFailure(item.evidence_id, f"Evidence confidence ({item.confidence}) is below threshold of {min_confidence}.")
            if not item.supporting_quote or not item.supporting_quote.quote:
                raise EvidenceValidationFailure(item.evidence_id, "Evidence item missing supporting quote reference.")

        return True
