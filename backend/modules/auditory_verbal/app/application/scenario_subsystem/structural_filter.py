"""
Guard 1: Structural Diversity Guard.
Compares StructuralFingerprint objects directly against session history to detect structural duplicates.
"""

from typing import List
from app.application.scenario_subsystem.assessment_specification import StructuralFingerprint


class StructuralDiversityGuard:
    """Evaluates structural fingerprint similarity before LLM invocation."""

    def __init__(self, similarity_threshold: float = 0.60):
        self.similarity_threshold = similarity_threshold

    def compute_fingerprint_similarity(
        self, fp1: StructuralFingerprint, fp2: StructuralFingerprint
    ) -> float:
        """Computes multi-dimensional structural similarity between two fingerprints."""
        matches = 0
        total_dimensions = 6

        if fp1.intent == fp2.intent:
            matches += 1.5
        if fp1.grammar == fp2.grammar:
            matches += 1.0
        if fp1.interaction == fp2.interaction:
            matches += 1.0
        if fp1.decision_type == fp2.decision_type:
            matches += 1.0
        if fp1.stakeholder_pattern == fp2.stakeholder_pattern:
            matches += 0.75
        if fp1.escalation_pattern == fp2.escalation_pattern:
            matches += 0.75

        return round(matches / (total_dimensions + 0.25), 3)

    def is_fingerprint_duplicate(
        self, candidate_fp: StructuralFingerprint, history: List[StructuralFingerprint]
    ) -> bool:
        """Returns True if candidate fingerprint matches any history item above threshold."""
        for past_fp in history:
            sim = self.compute_fingerprint_similarity(candidate_fp, past_fp)
            if sim >= self.similarity_threshold:
                return True
        return False
