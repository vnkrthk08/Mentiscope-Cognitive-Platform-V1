from typing import Dict, Any, List, Optional
from app.infrastructure.prompt_service import PromptOrchestrationResult
from app.application.construct_engine.models import (
    ConstructEvaluationSet,
    ConstructEvaluation,
    ConstructAssessment,
    ConstructEvidenceSummary,
)
from app.application.construct_engine.repository import ConstructRepository


class ConstructEvaluationBuilder:
    """Transforms validated APOS output payloads into immutable ConstructEvaluationSet aggregates."""

    def __init__(self, repository: Optional[ConstructRepository] = None):
        self.repository = repository or ConstructRepository()

    def build_evaluation_set(
        self,
        session_id: str,
        scenario_id: str,
        apos_result: PromptOrchestrationResult,
        summaries: List[ConstructEvidenceSummary],
    ) -> ConstructEvaluationSet:
        payload = apos_result.validated_response
        evals_raw = payload.get("construct_evaluations", [])

        evaluations: List[ConstructEvaluation] = []
        for item in evals_raw:
            c_name = item.get("construct", "DECISION_MAKING").upper()
            defn = self.repository.get_construct_definition(c_name)

            # Match supporting evidence IDs from summaries
            matching_summary = next((s for s in summaries if s.construct == c_name), None)
            supp_ids = matching_summary.evidence_references if matching_summary else []

            ev_obj = ConstructEvaluation(
                construct_name=c_name,
                construct_description=defn["description"],
                behavioral_summary=item.get("behavioral_summary", "Observed behavioral pattern."),
                supporting_evidence_ids=supp_ids,
                evaluation_narrative=item.get("evaluation_narrative", "Evidence demonstrates systematic behavior."),
                evaluation_confidence=float(item.get("confidence", 0.95)),
                prompt_version=apos_result.prompt_version,
                model_version=apos_result.selected_model,
            )
            evaluations.append(ev_obj)

        assessments: List[ConstructAssessment] = [
            ConstructAssessment(
                assessment_name=f"Qualitative Assessment for {e.construct_name}",
                interpretation=e.evaluation_narrative,
                strengths=[e.behavioral_summary],
                development_areas=[],
                supporting_evaluations=[e.evaluation_id],
            )
            for e in evaluations
        ]

        return ConstructEvaluationSet(
            session_id=session_id,
            scenario_id=scenario_id,
            evaluation_version="1.0.0",
            construct_evaluations=evaluations,
            assessments=assessments,
            evidence_summaries=summaries,
            evaluation_metadata={
                "provider": apos_result.selected_provider,
                "model": apos_result.selected_model,
                "latency_ms": apos_result.latency_ms,
            },
        )
