from typing import Dict, Any, List
from app.application.report_engine.models import (
    CandidateReport,
    CounselorReport,
    ResearchReport,
    AdministratorReport,
    AssessmentReport,
)


class ReportFormatter:
    """Derives multi-audience specialized presentation views from a single canonical AssessmentReport."""

    def format_candidate_view(self, report: AssessmentReport) -> CandidateReport:
        summary = f"Great effort completing the scenario assessment! Your overall outcome reflects '{report.decision_band}' competency."
        return CandidateReport(
            candidate_summary=summary,
            decision_band=report.decision_band,
            top_strengths=report.strengths,
            growth_areas=report.development_areas,
        )

    def format_counselor_view(self, report: AssessmentReport) -> CounselorReport:
        construct_narratives = {
            c_name: data.get("explanation", "") for c_name, data in report.construct_sections.items()
        }
        evidence_refs = [
            f"Evidence '{link.get('evidence_id')}' (Quote: '{link.get('verbatim_quote')}')"
            for link in report.evidence_traceability_map
        ]

        return CounselorReport(
            decision_explanation=report.executive_summary,
            construct_narratives=construct_narratives,
            behavioral_evidence_references=evidence_refs,
            reliability_notes=report.reliability_section.get("narrative", "High reliability score."),
        )

    def format_research_view(self, report: AssessmentReport) -> ResearchReport:
        return ResearchReport(
            pipeline_version=report.version_metadata.get("pipeline_version", "1.0.0"),
            calibration_version=report.version_metadata.get("calibration_model_version", "1.0.0"),
            prompt_versions={"EVIDENCE_EXTRACTION": "1.0.0", "CONSTRUCT_EVALUATION": "1.0.0"},
            model_versions={"LLM": "gemini-1.5-pro", "STT": "MockWhisper"},
            provenance_map={"traceability_links": report.evidence_traceability_map},
            reliability_statistics=report.reliability_section,
        )

    def format_administrator_view(self, report: AssessmentReport) -> AdministratorReport:
        return AdministratorReport(
            session_id=report.session_id,
            scenario_id=report.scenario_id,
            status="COMPLETED",
            completion_timestamp=report.created_at.isoformat(),
            audit_hash=report.explainability_metadata.get("reproducibility_hash", "AUDIT_OK"),
        )
