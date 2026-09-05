import uuid
from app.domain.entities.evidence import Evidence
from app.domain.value_objects.confidence_level import ConfidenceLevel
from app.domain.value_objects.enums import ConstructType, EvidenceType, PolarityType
from app.infrastructure.persistence.models.orm_models import BehavioralEvidenceORM


class EvidenceMapper:
    @staticmethod
    def to_orm(domain: Evidence) -> BehavioralEvidenceORM:
        return BehavioralEvidenceORM(
            id=str(domain.evidence_id),
            session_id=domain.session_id,
            prompt_id=domain.prompt_id,
            construct=domain.construct.value,
            quote=domain.quote,
            indicator_description=domain.indicator_description,
            confidence=domain.confidence.score,
            polarity=domain.polarity.value,
            evidence_type=domain.evidence_type.value,
        )

    @staticmethod
    def to_domain(orm: BehavioralEvidenceORM) -> Evidence:
        return Evidence(
            evidence_id=str(orm.id),
            session_id=orm.session_id,
            prompt_id=orm.prompt_id,
            construct=ConstructType(orm.construct),
            quote=orm.quote,
            indicator_description=orm.indicator_description,
            confidence=ConfidenceLevel(orm.confidence),
            polarity=PolarityType(orm.polarity),
            evidence_type=EvidenceType(orm.evidence_type),
            timestamp=orm.created_at,
        )
