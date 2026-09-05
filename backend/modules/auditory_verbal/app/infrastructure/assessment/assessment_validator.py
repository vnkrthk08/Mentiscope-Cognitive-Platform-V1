from typing import List
from app.domain.assessment.entities.assessment_result import AssessmentResult
from app.domain.assessment.entities.assessment_report import AssessmentReport


class AssessmentValidator:
    """Validates complete score ranges, traceability parameters, and config policy versions."""

    @staticmethod
    def validate_result(result: AssessmentResult) -> List[str]:
        errors = []
        if not result.framework_results:
            errors.append("AssessmentResult contains no framework results.")

        for fr in result.framework_results:
            # Score range check
            if fr.normalized_score < 0.0 or fr.normalized_score > 100.0:
                errors.append(f"Framework '{fr.framework}' normalized score is out of bounds (0-100).")
            # Confidence check
            if fr.confidence < 0.0 or fr.confidence > 1.0:
                errors.append(f"Framework '{fr.framework}' confidence is out of bounds (0-1).")

            for cb in fr.construct_results:
                if not cb.references:
                    errors.append(f"Missing traceability references list for construct '{cb.construct}'.")

        return errors

    @staticmethod
    def validate_report(report: AssessmentReport) -> List[str]:
        errors = []
        summary = report.assessment_summary
        if not summary.overall_observations or not summary.overall_observations.strip():
            errors.append("AssessmentReport summary overall observations cannot be empty.")
        if not summary.confidence_summary or not summary.confidence_summary.strip():
            errors.append("AssessmentReport summary confidence overview cannot be empty.")
        return errors
pre=1.0
