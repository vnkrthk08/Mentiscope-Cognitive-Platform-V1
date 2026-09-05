"""
Module: Constraint Validator (Assessment Assembly Engine v1.0).
Validates 11 strict psychometric, structural, and diversity constraints across assembled 5-scenario assessments.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional
from app.application.scenario_subsystem.scenario_metadata import ScenarioMetadata
from app.application.scenario_subsystem.assessment_blueprint import AssessmentBlueprint


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    rule_results: Dict[str, bool]
    offending_slot_index: Optional[int]
    violation_reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "rule_results": self.rule_results,
            "offending_slot_index": self.offending_slot_index,
            "violation_reason": self.violation_reason,
        }


class ConstraintValidator:
    """Enforces 11 strict rules across assembled 5-scenario assessments."""

    DIFFICULTY_RANK = {
        "EASY": 1,
        "EASY_MEDIUM": 2,
        "MEDIUM": 3,
        "MEDIUM_HARD": 4,
        "HARD": 5,
    }

    def validate_assessment(
        self,
        metadata_list: List[ScenarioMetadata],
        blueprint: AssessmentBlueprint,
    ) -> ValidationResult:

        rule_results: Dict[str, bool] = {}
        offending_slot: Optional[int] = None
        reason: str = "All constraints satisfied."

        if len(metadata_list) != 5:
            return ValidationResult(
                is_valid=False,
                rule_results={"LEN_5": False},
                offending_slot_index=None,
                violation_reason=f"Assessment must contain exactly 5 scenarios, got {len(metadata_list)}.",
            )

        # 1. NO_DUPLICATE_FAMILY
        families = [m.family_id for m in metadata_list]
        rule_results["NO_DUPLICATE_FAMILY"] = (len(set(families)) == 5)
        if not rule_results["NO_DUPLICATE_FAMILY"]:
            for i, f in enumerate(families):
                if families.count(f) > 1:
                    offending_slot = i
                    reason = f"Duplicate family ID '{f}' found at slot {i + 1}."
                    break

        # 2. NO_DUPLICATE_VARIANT
        variants = [m.variant_id for m in metadata_list]
        rule_results["NO_DUPLICATE_VARIANT"] = (len(set(variants)) == 5)
        if not rule_results["NO_DUPLICATE_VARIANT"] and offending_slot is None:
            offending_slot = 1
            reason = "Duplicate variant found."

        # 3. NO_DUPLICATE_CATEGORY
        categories = [m.category for m in metadata_list]
        rule_results["NO_DUPLICATE_CATEGORY"] = (len(set(categories)) == 5)
        if not rule_results["NO_DUPLICATE_CATEGORY"] and offending_slot is None:
            for i, c in enumerate(categories):
                if categories.count(c) > 1:
                    offending_slot = i
                    reason = f"Duplicate category '{c}' found at slot {i + 1}."
                    break

        # 4. CONSTRUCT_COVERAGE
        all_constructs: List[str] = []
        for m in metadata_list:
            all_constructs.extend(m.primary_constructs)
            all_constructs.extend(m.secondary_constructs)
        distinct_constructs = set(all_constructs)
        rule_results["CONSTRUCT_COVERAGE"] = (len(distinct_constructs) >= 5)

        # 5. STAKEHOLDER_DIVERSITY (>= 3 distinct)
        stakeholders = set(m.stakeholder_type.value for m in metadata_list)
        rule_results["STAKEHOLDER_DIVERSITY"] = (len(stakeholders) >= 3)

        # 6. INTERACTION_DIVERSITY (>= 3 distinct)
        interactions = set(m.interaction_type.value for m in metadata_list)
        rule_results["INTERACTION_DIVERSITY"] = (len(interactions) >= 3)

        # 7. COMMUNICATION_DIVERSITY (>= 3 distinct)
        comm_styles = set(m.communication_style.value for m in metadata_list)
        rule_results["COMMUNICATION_DIVERSITY"] = (len(comm_styles) >= 3)

        # 8. DECISION_DIVERSITY (>= 3 distinct)
        dec_types = set(m.decision_type.value for m in metadata_list)
        rule_results["DECISION_DIVERSITY"] = (len(dec_types) >= 3)

        # 9. PROGRESSIVE_DIFFICULTY (Monotonic S1 <= S2 <= S3 <= S4 <= S5)
        diff_ranks = [self.DIFFICULTY_RANK.get(m.listening_difficulty, 3) for m in metadata_list]
        is_monotonic = all(diff_ranks[i] <= diff_ranks[i + 1] for i in range(len(diff_ranks) - 1))
        rule_results["PROGRESSIVE_DIFFICULTY"] = is_monotonic
        if not is_monotonic and offending_slot is None:
            for i in range(len(diff_ranks) - 1):
                if diff_ranks[i] > diff_ranks[i + 1]:
                    offending_slot = i + 1
                    reason = f"Difficulty progression non-monotonic between slot {i + 1} and slot {i + 2}."
                    break

        # 10. COGNITIVE_PROCESS_BALANCE
        all_cognitive = set(p for m in metadata_list for p in m.cognitive_processes)
        rule_results["COGNITIVE_PROCESS_BALANCE"] = (len(all_cognitive) >= 2)

        # 11. ETHICAL_EXPOSURE_BALANCE (>= 1 ethical)
        ethical_count = sum(1 for m in metadata_list if m.ethical_dimension)
        rule_results["ETHICAL_EXPOSURE_BALANCE"] = (ethical_count >= 1)

        is_valid = all(rule_results.values())
        return ValidationResult(
            is_valid=is_valid,
            rule_results=rule_results,
            offending_slot_index=offending_slot if not is_valid else None,
            violation_reason=reason if not is_valid else "All constraints satisfied.",
        )
