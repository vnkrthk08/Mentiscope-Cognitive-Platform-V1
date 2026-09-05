import uuid
from app.domain.entities.assessment_report import AssessmentReport
from app.domain.entities.metric import Metric
from app.infrastructure.persistence.models.orm_models import AssessmentReportORM
from app.infrastructure.persistence.mappers.evidence_mapper import EvidenceMapper


class ReportMapper:
    @staticmethod
    def to_orm(domain: AssessmentReport) -> AssessmentReportORM:
        return AssessmentReportORM(
            id=str(domain.report_id),
            session_id=domain.session_id,
            candidate_id=domain.candidate_id,
            scenario_id=domain.scenario_id,
            overall_cognitive_index=domain.overall_cognitive_index,
            listening_metrics=[
                {"name": m.name, "value": m.value, "metadata": m.metadata} for m in domain.listening_metrics
            ],
            speaking_metrics=[
                {"name": m.name, "value": m.value, "metadata": m.metadata} for m in domain.speaking_metrics
            ],
            construct_scores=domain.construct_scores,
            evidence_summary=[
                {
                    "evidence_id": e.evidence_id,
                    "session_id": e.session_id,
                    "prompt_id": e.prompt_id,
                    "construct": e.construct.value,
                    "quote": e.quote,
                    "indicator_description": e.indicator_description,
                    "confidence": e.confidence.score,
                    "polarity": e.polarity.value,
                    "evidence_type": e.evidence_type.value,
                }
                for e in domain.evidence_summary
            ],
            recommendations=domain.recommendations,
            generated_at=domain.generated_at,
        )

    @staticmethod
    def to_domain(orm: AssessmentReportORM) -> AssessmentReport:
        from app.domain.entities.evidence import Evidence
        from app.domain.value_objects.confidence_level import ConfidenceLevel
        from app.domain.value_objects.enums import ConstructType, EvidenceType, PolarityType

        evidence_items = []
        for e in orm.evidence_summary:
            evidence_items.append(
                Evidence(
                    evidence_id=e["evidence_id"],
                    session_id=e["session_id"],
                    prompt_id=e["prompt_id"],
                    construct=ConstructType(e["construct"]),
                    quote=e["quote"],
                    indicator_description=e["indicator_description"],
                    confidence=ConfidenceLevel(e["confidence"]),
                    polarity=PolarityType(e["polarity"]),
                    evidence_type=EvidenceType(e["evidence_type"]),
                )
            )

        return AssessmentReport(
            report_id=str(orm.id),
            session_id=orm.session_id,
            candidate_id=orm.candidate_id,
            scenario_id=orm.scenario_id,
            overall_cognitive_index=orm.overall_cognitive_index,
            listening_metrics=[
                Metric(name=m["name"], value=m["value"], metadata=m.get("metadata", {})) for m in orm.listening_metrics
            ],
            speaking_metrics=[
                Metric(name=m["name"], value=m["value"], metadata=m.get("metadata", {})) for m in orm.speaking_metrics
            ],
            construct_scores=orm.construct_scores,
            evidence_summary=evidence_items,
            recommendations=orm.recommendations,
            generated_at=orm.generated_at,
        )
