"""
Module: Assessment Builder (Assessment Assembly Engine v1.0).
Constructs the complete 5-scenario runtime Assessment object.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.domain.entities.scenario import Scenario
from app.application.scenario_subsystem.scenario_metadata import ScenarioMetadata
from app.application.scenario_subsystem.assessment_audit import AssessmentAuditReport


@dataclass
class Assessment:
    assessment_id: str
    candidate_id: str
    scenario_1: Scenario
    scenario_2: Scenario
    scenario_3: Scenario
    scenario_4: Scenario
    scenario_5: Scenario
    coverage_matrix: Dict[str, int]
    difficulty_curve: List[str]
    metadata: Dict[str, Any]
    audit_report: AssessmentAuditReport

    def get_scenarios(self) -> List[Scenario]:
        return [self.scenario_1, self.scenario_2, self.scenario_3, self.scenario_4, self.scenario_5]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "candidate_id": self.candidate_id,
            "scenarios": [s.to_dict() for s in self.get_scenarios()],
            "coverage_matrix": self.coverage_matrix,
            "difficulty_curve": self.difficulty_curve,
            "metadata": self.metadata,
            "audit_report": self.audit_report.to_dict(),
        }


class AssessmentBuilder:
    """Builds the Assessment runtime object from 5 selected scenarios and metadata."""

    def build_assessment(
        self,
        assessment_id: str,
        candidate_id: str,
        scenarios: List[Scenario],
        metadata_list: List[ScenarioMetadata],
        coverage_matrix: Dict[str, int],
        audit_report: AssessmentAuditReport,
    ) -> Assessment:

        if len(scenarios) != 5 or len(metadata_list) != 5:
            raise ValueError("AssessmentBuilder requires exactly 5 scenarios and 5 metadata items.")

        difficulty_curve = [m.listening_difficulty for m in metadata_list]

        return Assessment(
            assessment_id=assessment_id,
            candidate_id=candidate_id,
            scenario_1=scenarios[0],
            scenario_2=scenarios[1],
            scenario_3=scenarios[2],
            scenario_4=scenarios[3],
            scenario_5=scenarios[4],
            coverage_matrix=coverage_matrix,
            difficulty_curve=difficulty_curve,
            metadata={
                "assembly_engine": "v1.0",
                "total_scenarios": 5,
                "families": [m.family_id for m in metadata_list],
            },
            audit_report=audit_report,
        )
