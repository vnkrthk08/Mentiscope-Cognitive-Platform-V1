"""
Module: Assessment Audit Report (Assessment Assembly Engine v1.0).
Generates deterministic, auditable, and reproducible assessment creation reports.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


@dataclass(frozen=True)
class AssessmentAuditReport:
    assessment_id: str
    candidate_id: str
    scenario_ids: List[str]
    family_ids: List[str]
    construct_coverage_matrix: Dict[str, int]
    category_distribution: Dict[str, int]
    difficulty_curve: List[str]
    stakeholder_distribution: Dict[str, int]
    decision_type_distribution: Dict[str, int]
    interaction_distribution: Dict[str, int]
    communication_distribution: Dict[str, int]
    constraint_validation_report: Dict[str, bool]
    assembly_timestamp: str
    assembly_version: str
    random_seed: Optional[int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "candidate_id": self.candidate_id,
            "scenario_ids": self.scenario_ids,
            "family_ids": self.family_ids,
            "construct_coverage_matrix": self.construct_coverage_matrix,
            "category_distribution": self.category_distribution,
            "difficulty_curve": self.difficulty_curve,
            "stakeholder_distribution": self.stakeholder_distribution,
            "decision_type_distribution": self.decision_type_distribution,
            "interaction_distribution": self.interaction_distribution,
            "communication_distribution": self.communication_distribution,
            "constraint_validation_report": self.constraint_validation_report,
            "assembly_timestamp": self.assembly_timestamp,
            "assembly_version": self.assembly_version,
            "random_seed": self.random_seed,
        }
