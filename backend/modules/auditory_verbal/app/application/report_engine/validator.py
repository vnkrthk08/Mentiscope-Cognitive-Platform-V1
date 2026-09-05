from app.application.report_engine.models import AssessmentReport
from app.domain.exceptions.report_exceptions import ReportValidationFailure


class ReportValidator:
    """Validates canonical AssessmentReport structure, traceability completeness, and section integrity."""

    def validate_report(self, report: AssessmentReport) -> bool:
        if not report.executive_summary or not report.executive_summary.strip():
            raise ReportValidationFailure(report.report_id, "Executive summary is empty.")

        if not report.construct_sections:
            raise ReportValidationFailure(report.report_id, "Report contains no construct sections.")

        if not report.evidence_traceability_map:
            raise ReportValidationFailure(report.report_id, "Evidence traceability map is empty.")

        if not report.candidate_view or not report.counselor_view or not report.research_view or not report.administrator_view:
            raise ReportValidationFailure(report.report_id, "Report is missing one or more multi-audience presentation views.")

        return True
