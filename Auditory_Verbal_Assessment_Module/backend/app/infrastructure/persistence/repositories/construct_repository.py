from typing import List, Dict, Any, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.persistence.models.orm_models import ConstructEvaluationORM
from app.application.construct_engine.models import ConstructEvaluation


class ConstructRepository:
    """SQLAlchemy and memory fallback repository for construct definitions and construct evaluations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._construct_definitions: Dict[str, Dict[str, Any]] = {
            "DECISION_MAKING": {
                "name": "Decision Making",
                "description": "Evaluates logical prioritization, risk assessment, and systematic problem solving under pressure.",
                "indicators": ["Emergency Protocol Initiation", "Safety Prioritization", "Risk Mitigation"],
            },
            "COMMUNICATION": {
                "name": "Communication Clarity",
                "description": "Evaluates oral fluency, sequential explanation, and structured argumentation.",
                "indicators": ["Logical Sequencing", "Articulate Response", "Clarity of Expression"],
            },
            "WORKING_MEMORY": {
                "name": "Working Memory Capacity",
                "description": "Evaluates retention and processing of auditory information under temporal constraints.",
                "indicators": ["Detail Retention", "Sequential Recall"],
            },
        }

    def get_construct_definition(self, construct_name: str) -> Dict[str, Any]:
        defn = self._construct_definitions.get(construct_name.upper())
        if not defn:
            return {
                "name": construct_name,
                "description": f"Psychometric construct evaluation for {construct_name}",
                "indicators": ["Observed behavior"],
            }
        return defn

    async def save_evaluation(self, session_id: str, evaluation: ConstructEvaluation) -> ConstructEvaluationORM:
        orm = ConstructEvaluationORM(
            id=uuid.UUID(evaluation.evaluation_id) if len(evaluation.evaluation_id) == 36 else uuid.uuid4(),
            session_id=session_id,
            construct_name=evaluation.construct_name,
            construct_description=evaluation.construct_description,
            behavioral_summary=evaluation.behavioral_summary,
            supporting_evidence_ids=evaluation.supporting_evidence_ids,
            evaluation_narrative=evaluation.evaluation_narrative,
            evaluation_confidence=evaluation.evaluation_confidence,
            prompt_version=evaluation.prompt_version,
            model_version=evaluation.model_version,
        )
        self.session.add(orm)
        await self.session.flush()
        return orm

    async def get_evaluations_by_session_id(self, session_id: str) -> List[ConstructEvaluation]:
        result = await self.session.execute(
            select(ConstructEvaluationORM).where(
                ConstructEvaluationORM.session_id == session_id, ConstructEvaluationORM.is_deleted == False
            )
        )
        evals = []
        for orm in result.scalars().all():
            evals.append(
                ConstructEvaluation(
                    evaluation_id=str(orm.id),
                    construct_name=orm.construct_name,
                    construct_description=orm.construct_description,
                    behavioral_summary=orm.behavioral_summary,
                    supporting_evidence_ids=orm.supporting_evidence_ids,
                    evaluation_narrative=orm.evaluation_narrative,
                    evaluation_confidence=orm.evaluation_confidence,
                    prompt_version=orm.prompt_version,
                    model_version=orm.model_version,
                )
            )
        return evals
