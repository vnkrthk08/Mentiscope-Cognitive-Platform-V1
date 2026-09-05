import uuid
from datetime import datetime, timezone
from typing import List
from app.domain.assessment.entities.assessment_report import AssessmentReport
from app.domain.assessment.entities.assessment_result import AssessmentResult
from app.domain.assessment.entities.assessment_summary import AssessmentSummary
from app.domain.assessment.value_objects.report_metadata import ReportMetadata


class AssessmentReportBuilder:
    """Builder class constructing structured explainable AssessmentReport instances from calculated results."""

    @staticmethod
    def build_report(result: AssessmentResult) -> AssessmentReport:
        # Create qualitative summaries
        overview = {}
        strengths = []
        improvements = []

        for fr in result.framework_results:
            overview[fr.framework] = fr.summary
            # Map strengths/improvements based on normalized score threshold
            for cb in fr.construct_results:
                if cb.normalized_score >= 70.0:
                    strengths.append(f"High proficiency demonstrated in construct: {cb.construct}")
                else:
                    improvements.append(f"Opportunity to develop competency in construct: {cb.construct}")

        summary = AssessmentSummary(
            framework_overview=overview,
            strengths=strengths if strengths else ["Demonstrates consistent baseline proficiency."],
            areas_for_improvement=improvements if improvements else ["Continue building advanced capabilities."],
            confidence_summary=f"Overall evaluation confidence estimated at {result.overall_confidence:.2f}.",
            overall_observations="Detailed audit record showing candidate constructs profiling.",
        )

        meta = ReportMetadata(
            generated_by="AssessmentScoringEngine",
            pipeline_version="1.0.0",
            engine_version="1.0.0",
            report_version="1.0.0",
            language="en",
        )

        return AssessmentReport(
            report_id=str(uuid.uuid4()),
            assessment_result_id=result.result_id,
            candidate_id=result.candidate_id,
            assessment_id=result.assessment_id,
            assessment_summary=summary,
            framework_results=result.framework_results,
            report_metadata=meta,
        )
pre=1.0
