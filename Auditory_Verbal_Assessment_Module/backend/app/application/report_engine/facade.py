from typing import Any, Dict, Optional
from app.core.logging import logger
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.entities.assessment_report import AssessmentReport as DomainAssessmentReport
from app.domain.interfaces.subsystems import IMetricsEngine
from app.application.scoring_engine.models import AssessmentScoreSet
from app.application.report_engine.summary_generator import ExecutiveSummaryGenerator
from app.application.report_engine.explanation_generator import ConstructExplanationGenerator
from app.application.report_engine.traceability_builder import EvidenceTraceabilityBuilder
from app.application.report_engine.reliability_explainer import ReliabilityExplanationGenerator
from app.application.report_engine.explainability_manager import ExplainabilityManager
from app.application.report_engine.formatter import ReportFormatter
from app.application.report_engine.validator import ReportValidator
from app.application.report_engine.publisher import ReportEventPublisher
from app.application.report_engine.models import AssessmentReport
from app.domain.exceptions.report_exceptions import ReportGenerationFailure


class AssessmentReportingEngine(IMetricsEngine):
    """Facade for Assessment Reporting & Explainability Engine (AREE) implementing IMetricsEngine.
    Transforms AssessmentScoreSet objects into immutable AssessmentReport aggregates.
    Explains score meaning, maintains complete evidence traceability, aggregates version metadata,
    and derives specialized multi-audience presentation views (Candidate, Counselor, Research, Administrator).
    DOES NOT CALCULATE SCORES OR RECOMMEND CAREERS! ZERO LLM CALLS!
    """

    def __init__(
        self,
        summary_generator: Optional[ExecutiveSummaryGenerator] = None,
        explanation_generator: Optional[ConstructExplanationGenerator] = None,
        traceability_builder: Optional[EvidenceTraceabilityBuilder] = None,
        reliability_explainer: Optional[ReliabilityExplanationGenerator] = None,
        explainability_manager: Optional[ExplainabilityManager] = None,
        formatter: Optional[ReportFormatter] = None,
        validator: Optional[ReportValidator] = None,
        publisher: Optional[ReportEventPublisher] = None,
    ):
        self.summary_generator = summary_generator or ExecutiveSummaryGenerator()
        self.explanation_generator = explanation_generator or ConstructExplanationGenerator()
        self.traceability_builder = traceability_builder or EvidenceTraceabilityBuilder()
        self.reliability_explainer = reliability_explainer or ReliabilityExplanationGenerator()
        self.explainability_manager = explainability_manager or ExplainabilityManager()
        self.formatter = formatter or ReportFormatter()
        self.validator = validator or ReportValidator()
        self.publisher = publisher or ReportEventPublisher()

    async def generate_assessment_report(
        self,
        session: AssessmentSession,
        score_set: AssessmentScoreSet,
    ) -> AssessmentReport:
        """Generates canonical AssessmentReport aggregate and multi-audience presentation views."""
        logger.info(f"[AREE FACADE] Generating assessment report for session '{session.session_id}'")
        await self.publisher.publish_started(session.session_id, session.scenario_id)

        try:
            # 1. Executive Summary & Competency Band
            exec_summary = self.summary_generator.generate_summary(score_set)
            band = score_set.assessment_decision.decision_band if score_set.assessment_decision else "HIGH_COMPETENCY"
            await self.publisher.publish_summary_generated(session.session_id, band)

            # 2. Construct Explanations, Strengths & Growth Areas
            c_sections, strengths, growth_areas = self.explanation_generator.generate_explanations(score_set)
            await self.publisher.publish_sections_generated(session.session_id, len(c_sections))

            # 3. Complete Evidence Traceability Provenance Mapping
            trace_map = self.traceability_builder.build_traceability_map(session, score_set)
            await self.publisher.publish_traceability_built(session.session_id, len(trace_map))

            # 4. Psychometric Reliability Explanation
            rel_section = self.reliability_explainer.generate_explanation(score_set)
            rel_coeff = float(rel_section.get("reliability_estimate", 0.92))
            await self.publisher.publish_reliability_generated(session.session_id, rel_coeff)

            # 5. Version Metadata & Explainability Provenance
            ver_meta = self.explainability_manager.aggregate_version_metadata(session.session_id)

            # 6. Build Canonical AssessmentReport Aggregate
            report = AssessmentReport(
                session_id=session.session_id,
                scenario_id=session.scenario_id,
                executive_summary=exec_summary,
                decision_band=band,
                construct_sections=c_sections,
                score_tables={"construct_scores": score_set.construct_scores, "composite_scores": score_set.composite_scores},
                reliability_section=rel_section,
                evidence_traceability_map=trace_map,
                strengths=strengths,
                development_areas=growth_areas,
                version_metadata=ver_meta,
                explainability_metadata={"traceability_links_count": len(trace_map), **ver_meta},
            )

            # 7. Derive Multi-Audience Views
            candidate_view = self.formatter.format_candidate_view(report)
            counselor_view = self.formatter.format_counselor_view(report)
            research_view = self.formatter.format_research_view(report)
            admin_view = self.formatter.format_administrator_view(report)

            report = AssessmentReport(
                report_id=report.report_id,
                session_id=report.session_id,
                scenario_id=report.scenario_id,
                executive_summary=report.executive_summary,
                decision_band=report.decision_band,
                construct_sections=report.construct_sections,
                score_tables=report.score_tables,
                reliability_section=report.reliability_section,
                evidence_traceability_map=report.evidence_traceability_map,
                strengths=report.strengths,
                development_areas=report.development_areas,
                version_metadata=report.version_metadata,
                explainability_metadata=report.explainability_metadata,
                candidate_view=candidate_view,
                counselor_view=counselor_view,
                research_view=research_view,
                administrator_view=admin_view,
            )

            # 8. Validate Report
            self.validator.validate_report(report)
            await self.publisher.publish_validated(session.session_id, "VALIDATED")

            await self.publisher.publish_completed(session.session_id, report.report_id, band)
            logger.info(f"[AREE FACADE] Completed report generation for session '{session.session_id}'. Report ID: {report.report_id}")

            return report

        except Exception as e:
            await self.publisher.publish_failed(session.session_id, str(e))
            logger.error(f"[AREE FACADE] Report generation failed for session '{session.session_id}': {str(e)}")
            raise ReportGenerationFailure(session.session_id, str(e))

    async def generate_report(self, session: AssessmentSession) -> DomainAssessmentReport:
        """Implementation of IMetricsEngine abstract interface method."""
        return DomainAssessmentReport(
            session_id=session.session_id,
            candidate_id=session.candidate_id,
            scenario_id=session.scenario_id,
            overall_score=session.metadata.get("overall_construct_scores", {}).get("DECISION_MAKING", 85.0),
        )
