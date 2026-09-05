"""
DatasetService — Application Service.

Builds ValidationDataset records from completed assessment pipeline
artifacts. Queries existing sprint data (transcripts, behavior evidence,
construct evaluations, ASR reports) and assembles them into exportable
research records.

This service ONLY reads from completed pipeline data.
It NEVER modifies assessment scores or results.
"""
from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.domain.research.entities.validation_dataset import ValidationDataset
from app.domain.research.value_objects.research_metadata import ResearchMetadata
from app.application.research.events.research_events import ValidationDatasetBuilt


class DatasetService:
    """
    Application service for building and managing ValidationDatasets.

    Reads-only from the existing assessment pipeline tables.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def build_dataset(
        self,
        candidate_id: str,
        assessment_id: str,
        session_id: str,
        scenario_id: str,
        pipeline_version: str = "1.0.0",
        model_version: str = "gemini-1.5-pro",
        prompt_version: str = "1.0.0",
        scoring_policy_version: str = "1.0.0",
        notes: Optional[str] = None,
    ) -> ValidationDataset:
        """
        Build a ValidationDataset by aggregating all pipeline artifacts
        for a completed assessment session.
        """
        start_ms = time.monotonic() * 1000

        logger.info(
            "[PVCSF DatasetService] Building validation dataset",
            candidate_id=candidate_id,
            session_id=session_id,
        )

        # 1. Fetch transcript
        transcript_text, transcript_confidence = await self._fetch_transcript(session_id)

        # 2. Fetch behavioral evidence
        behavior_evidence, behavior_confidence, observation_count = \
            await self._fetch_behavior_evidence(session_id)

        # 3. Fetch construct evaluations
        construct_evaluations, construct_confidence_scores, frameworks_evaluated = \
            await self._fetch_construct_evaluations(session_id)

        # 4. Fetch assessment scores / report
        ai_scores, composite_score, score_confidence, norm_method, \
            evidence_references = await self._fetch_assessment_scores(
                candidate_id, assessment_id
            )

        # 5. Build metadata VO
        metadata = ResearchMetadata(
            pipeline_version=pipeline_version,
            model_version=model_version,
            prompt_version=prompt_version,
            scoring_policy_version=scoring_policy_version,
            notes=notes,
        )

        # 6. Assemble domain entity
        dataset = ValidationDataset(
            dataset_id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            assessment_id=assessment_id,
            scenario_id=scenario_id,
            session_id=session_id,
            transcript_text=transcript_text,
            transcript_confidence=transcript_confidence,
            behavior_evidence=behavior_evidence,
            behavior_confidence=behavior_confidence,
            observation_count=observation_count,
            construct_evaluations=construct_evaluations,
            construct_confidence_scores=construct_confidence_scores,
            frameworks_evaluated=frameworks_evaluated,
            ai_framework_scores=ai_scores,
            ai_composite_score=composite_score,
            score_confidence=score_confidence,
            normalization_method=norm_method,
            evidence_references=evidence_references,
            metadata=metadata,
        )

        # 7. Mark READY if complete, DRAFT if data is partial
        missing = dataset.validate_completeness()
        if not missing:
            dataset.status = "READY"
        else:
            logger.warning(
                "[PVCSF DatasetService] Dataset is partial — missing fields",
                missing=missing,
                dataset_id=dataset.dataset_id,
            )
            dataset.status = "DRAFT"

        elapsed_ms = (time.monotonic() * 1000) - start_ms
        logger.info(
            "[PVCSF DatasetService] Dataset built",
            dataset_id=dataset.dataset_id,
            status=dataset.status,
            elapsed_ms=round(elapsed_ms, 2),
        )

        return dataset

    # ---------------------------------------------------------------------------
    # Private helpers — read-only queries on existing pipeline tables
    # ---------------------------------------------------------------------------

    async def _fetch_transcript(self, session_id: str) -> tuple[str, float]:
        """Fetch transcript text and confidence from transcripts table."""
        from app.infrastructure.persistence.models.orm_models import TranscriptORM
        from sqlalchemy import select

        result = await self._session.execute(
            select(TranscriptORM)
            .where(
                TranscriptORM.session_id == session_id,
                TranscriptORM.is_deleted == False,
            )
            .order_by(TranscriptORM.created_at.desc())
            .limit(1)
        )
        orm = result.scalars().first()
        if orm:
            return orm.transcript_text, orm.confidence_score
        return "", 0.0

    async def _fetch_behavior_evidence(
        self, session_id: str
    ) -> tuple[List[Dict[str, Any]], float, int]:
        """Aggregate behavioral evidence observations for the session."""
        from app.infrastructure.persistence.models.orm_models import BehavioralEvidenceORM

        result = await self._session.execute(
            select(BehavioralEvidenceORM).where(
                BehavioralEvidenceORM.session_id == session_id,
                BehavioralEvidenceORM.is_deleted == False,
            )
        )
        records = result.scalars().all()
        if not records:
            return [], 0.0, 0

        evidence_list = [
            {
                "construct": r.construct,
                "quote": r.quote,
                "indicator": r.indicator_description,
                "confidence": r.confidence,
                "polarity": r.polarity,
                "evidence_type": r.evidence_type,
            }
            for r in records
        ]
        avg_confidence = sum(r.confidence for r in records) / len(records)
        return evidence_list, round(avg_confidence, 4), len(records)

    async def _fetch_construct_evaluations(
        self, session_id: str
    ) -> tuple[List[Dict[str, Any]], Dict[str, float], List[str]]:
        """Fetch construct evaluation summaries for the session."""
        from app.infrastructure.persistence.models.orm_models import ConstructEvaluationORM

        result = await self._session.execute(
            select(ConstructEvaluationORM).where(
                ConstructEvaluationORM.session_id == session_id,
                ConstructEvaluationORM.is_deleted == False,
            )
        )
        records = result.scalars().all()
        if not records:
            return [], {}, []

        evaluations = [
            {
                "construct_name": r.construct_name,
                "construct_description": r.construct_description,
                "behavioral_summary": r.behavioral_summary,
                "evaluation_narrative": r.evaluation_narrative,
                "confidence": r.evaluation_confidence,
                "prompt_version": r.prompt_version,
                "model_version": r.model_version,
            }
            for r in records
        ]
        confidence_scores = {r.construct_name: r.evaluation_confidence for r in records}
        frameworks: List[str] = list({r.construct_name.split("_")[0] for r in records if "_" in r.construct_name})
        if not frameworks:
            frameworks = ["GENERAL"]

        return evaluations, confidence_scores, frameworks

    async def _fetch_assessment_scores(
        self, candidate_id: str, assessment_id: str
    ) -> tuple[Dict[str, float], float, float, str, List[Dict[str, Any]]]:
        """Fetch assessment result scores from the ASR report table."""
        from app.infrastructure.assessment.orm_models import AssessmentReportORM

        try:
            assessment_uuid = uuid.UUID(assessment_id)
        except ValueError:
            return {}, 0.0, 0.0, "LINEAR", []

        result = await self._session.execute(
            select(AssessmentReportORM).where(
                AssessmentReportORM.assessment_id == assessment_uuid,
                AssessmentReportORM.candidate_id == candidate_id,
            ).order_by(AssessmentReportORM.created_at.desc()).limit(1)
        )
        orm = result.scalars().first()
        if not orm:
            return {}, 0.0, 0.0, "LINEAR", []

        # Extract flattened framework scores
        framework_scores: Dict[str, float] = {}
        evidence_refs: List[Dict[str, Any]] = []

        for fw in orm.framework_results:
            fw_name = fw.get("framework", "UNKNOWN")
            normalized = fw.get("normalized_score", 0.0)
            framework_scores[fw_name] = normalized
            for sb in fw.get("score_breakdowns", []):
                evidence_refs.append({
                    "framework": fw_name,
                    "construct": sb.get("construct_name", ""),
                    "raw_score": sb.get("raw_score", 0.0),
                    "normalized_score": sb.get("normalized_score", 0.0),
                    "evidence_count": sb.get("evidence_count", 0),
                })

        composite = (
            sum(framework_scores.values()) / len(framework_scores)
            if framework_scores else 0.0
        )
        norm_method = orm.report_metadata.get("normalization_method", "LINEAR")
        confidence = orm.report_metadata.get("average_confidence", 0.0)

        return framework_scores, round(composite, 4), confidence, norm_method, evidence_refs
