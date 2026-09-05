"""
PVCSF Infrastructure Repositories.

SQLAlchemy 2.x async repositories for all four PVCSF aggregates:
  - ValidationDatasetRepository
  - ExpertReviewRepository
  - CalibrationBatchRepository
  - ResearchExportRepository
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.research.entities.calibration_batch import CalibrationBatch
from app.domain.research.entities.expert_review import ExpertReview
from app.domain.research.entities.research_export import ResearchExport
from app.domain.research.entities.validation_dataset import ValidationDataset
from app.domain.research.value_objects.agreement_metrics import AgreementMetrics
from app.domain.research.value_objects.calibration_metadata import CalibrationMetadata
from app.domain.research.value_objects.research_metadata import ResearchMetadata
from app.infrastructure.research.orm_models import (
    CalibrationBatchORM,
    ExpertReviewORM,
    PVCSFMetricORM,
    ResearchExportORM,
    ValidationDatasetORM,
)


# ---------------------------------------------------------------------------
# ValidationDataset Repository
# ---------------------------------------------------------------------------

class ValidationDatasetRepository:
    """Repository for ValidationDataset CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, dataset: ValidationDataset) -> ValidationDatasetORM:
        """Persist or update a ValidationDataset."""
        try:
            existing_id = uuid.UUID(dataset.dataset_id)
        except ValueError:
            existing_id = uuid.uuid4()

        existing = await self._session.get(ValidationDatasetORM, existing_id)
        if existing:
            # Update
            existing.transcript_text = dataset.transcript_text
            existing.transcript_confidence = dataset.transcript_confidence
            existing.behavior_evidence = dataset.behavior_evidence
            existing.behavior_confidence = dataset.behavior_confidence
            existing.observation_count = dataset.observation_count
            existing.construct_evaluations = dataset.construct_evaluations
            existing.construct_confidence_scores = dataset.construct_confidence_scores
            existing.frameworks_evaluated = dataset.frameworks_evaluated
            existing.ai_framework_scores = dataset.ai_framework_scores
            existing.ai_composite_score = dataset.ai_composite_score
            existing.score_confidence = dataset.score_confidence
            existing.normalization_method = dataset.normalization_method
            existing.evidence_references = dataset.evidence_references
            existing.expert_ratings = dataset.expert_ratings
            existing.reviewer_notes = dataset.reviewer_notes
            existing.review_status = dataset.review_status
            existing.research_metadata = dataset.metadata.to_dict() if dataset.metadata else {}
            existing.status = dataset.status
            existing.updated_at = datetime.now(timezone.utc)
            await self._session.flush()
            return existing
        else:
            orm = ValidationDatasetORM(
                id=existing_id,
                candidate_id=dataset.candidate_id,
                assessment_id=dataset.assessment_id,
                scenario_id=dataset.scenario_id,
                session_id=dataset.session_id,
                transcript_text=dataset.transcript_text,
                transcript_confidence=dataset.transcript_confidence,
                audio_asset_id=dataset.audio_asset_id,
                audio_duration_seconds=dataset.audio_duration_seconds,
                behavior_evidence=dataset.behavior_evidence,
                behavior_confidence=dataset.behavior_confidence,
                observation_count=dataset.observation_count,
                construct_evaluations=dataset.construct_evaluations,
                construct_confidence_scores=dataset.construct_confidence_scores,
                frameworks_evaluated=dataset.frameworks_evaluated,
                ai_framework_scores=dataset.ai_framework_scores,
                ai_composite_score=dataset.ai_composite_score,
                score_confidence=dataset.score_confidence,
                normalization_method=dataset.normalization_method,
                evidence_references=dataset.evidence_references,
                prompt_execution_id=dataset.prompt_execution_id,
                construct_mapping_ids=dataset.construct_mapping_ids,
                expert_ratings=dataset.expert_ratings,
                reviewer_notes=dataset.reviewer_notes,
                review_status=dataset.review_status,
                research_metadata=dataset.metadata.to_dict() if dataset.metadata else {},
                status=dataset.status,
            )
            self._session.add(orm)
            await self._session.flush()
            return orm

    async def get_by_id(self, dataset_id: str) -> Optional[ValidationDataset]:
        try:
            uid = uuid.UUID(dataset_id)
        except ValueError:
            return None
        orm = await self._session.get(ValidationDatasetORM, uid)
        if not orm or orm.is_deleted:
            return None
        return self._to_entity(orm)

    async def list_all(
        self,
        candidate_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ValidationDataset]:
        q = select(ValidationDatasetORM).where(ValidationDatasetORM.is_deleted == False)
        if candidate_id:
            q = q.where(ValidationDatasetORM.candidate_id == candidate_id)
        if status:
            q = q.where(ValidationDatasetORM.status == status)
        q = q.order_by(ValidationDatasetORM.created_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(q)
        return [self._to_entity(r) for r in result.scalars().all()]

    async def count(self, status: Optional[str] = None) -> int:
        q = select(func.count()).select_from(ValidationDatasetORM).where(
            ValidationDatasetORM.is_deleted == False
        )
        if status:
            q = q.where(ValidationDatasetORM.status == status)
        result = await self._session.execute(q)
        return result.scalar_one()

    async def get_by_ids(self, dataset_ids: List[str]) -> List[ValidationDataset]:
        """Bulk fetch by IDs."""
        try:
            uids = [uuid.UUID(did) for did in dataset_ids]
        except ValueError:
            return []
        result = await self._session.execute(
            select(ValidationDatasetORM).where(
                ValidationDatasetORM.id.in_(uids),
                ValidationDatasetORM.is_deleted == False,
            )
        )
        return [self._to_entity(r) for r in result.scalars().all()]

    def _to_entity(self, orm: ValidationDatasetORM) -> ValidationDataset:
        meta_dict = orm.research_metadata or {}
        metadata = None
        if meta_dict.get("pipeline_version"):
            try:
                metadata = ResearchMetadata(
                    pipeline_version=meta_dict.get("pipeline_version", "1.0.0"),
                    model_version=meta_dict.get("model_version", "unknown"),
                    prompt_version=meta_dict.get("prompt_version", "1.0.0"),
                    scoring_policy_version=meta_dict.get("scoring_policy_version", "1.0.0"),
                    notes=meta_dict.get("notes"),
                )
            except ValueError:
                metadata = None

        return ValidationDataset(
            dataset_id=str(orm.id),
            candidate_id=orm.candidate_id,
            assessment_id=orm.assessment_id,
            scenario_id=orm.scenario_id,
            session_id=orm.session_id,
            transcript_text=orm.transcript_text,
            transcript_confidence=orm.transcript_confidence,
            audio_asset_id=orm.audio_asset_id,
            audio_duration_seconds=orm.audio_duration_seconds,
            behavior_evidence=orm.behavior_evidence,
            behavior_confidence=orm.behavior_confidence,
            observation_count=orm.observation_count,
            construct_evaluations=orm.construct_evaluations,
            construct_confidence_scores=orm.construct_confidence_scores,
            frameworks_evaluated=orm.frameworks_evaluated,
            ai_framework_scores=orm.ai_framework_scores,
            ai_composite_score=orm.ai_composite_score,
            score_confidence=orm.score_confidence,
            normalization_method=orm.normalization_method,
            evidence_references=orm.evidence_references,
            prompt_execution_id=orm.prompt_execution_id,
            construct_mapping_ids=orm.construct_mapping_ids,
            expert_ratings=orm.expert_ratings,
            reviewer_notes=orm.reviewer_notes,
            review_status=orm.review_status,
            metadata=metadata,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )


# ---------------------------------------------------------------------------
# ExpertReview Repository
# ---------------------------------------------------------------------------

class ExpertReviewRepository:
    """Repository for ExpertReview CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, review: ExpertReview) -> ExpertReviewORM:
        try:
            review_uuid = uuid.UUID(review.review_id)
        except ValueError:
            review_uuid = uuid.uuid4()

        orm = ExpertReviewORM(
            id=review_uuid,
            dataset_id=review.dataset_id,
            reviewer_id=review.reviewer_id,
            reviewer_name=review.reviewer_name,
            reviewer_credentials=review.reviewer_credentials,
            expert_construct_scores=review.expert_construct_scores,
            overall_score=review.overall_score,
            comments=review.comments,
            strengths=review.strengths,
            concerns=review.concerns,
            recommendations=review.recommendations,
            decision=review.decision,
            rejection_reason=review.rejection_reason,
            revision_notes=review.revision_notes,
            annotation_tags=review.annotation_tags,
            review_round=review.review_round,
            review_duration_minutes=review.review_duration_minutes,
            status=review.status,
            submitted_at=review.submitted_at,
            finalised_at=review.finalised_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return orm

    async def get_by_id(self, review_id: str) -> Optional[ExpertReview]:
        try:
            uid = uuid.UUID(review_id)
        except ValueError:
            return None
        orm = await self._session.get(ExpertReviewORM, uid)
        if not orm or orm.is_deleted:
            return None
        return self._to_entity(orm)

    async def list_by_dataset(self, dataset_id: str) -> List[ExpertReview]:
        result = await self._session.execute(
            select(ExpertReviewORM).where(
                ExpertReviewORM.dataset_id == dataset_id,
                ExpertReviewORM.is_deleted == False,
            ).order_by(ExpertReviewORM.created_at.desc())
        )
        return [self._to_entity(r) for r in result.scalars().all()]

    async def count_pending(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(ExpertReviewORM).where(
                ExpertReviewORM.status == "DRAFT",
                ExpertReviewORM.is_deleted == False,
            )
        )
        return result.scalar_one()

    async def count_approved(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(ExpertReviewORM).where(
                ExpertReviewORM.decision == "APPROVED",
                ExpertReviewORM.is_deleted == False,
            )
        )
        return result.scalar_one()

    def _to_entity(self, orm: ExpertReviewORM) -> ExpertReview:
        return ExpertReview(
            review_id=str(orm.id),
            dataset_id=orm.dataset_id,
            reviewer_id=orm.reviewer_id,
            reviewer_name=orm.reviewer_name,
            reviewer_credentials=orm.reviewer_credentials,
            expert_construct_scores=orm.expert_construct_scores,
            overall_score=orm.overall_score,
            comments=orm.comments,
            strengths=orm.strengths,
            concerns=orm.concerns,
            recommendations=orm.recommendations,
            decision=orm.decision,
            rejection_reason=orm.rejection_reason,
            revision_notes=orm.revision_notes,
            annotation_tags=orm.annotation_tags,
            review_round=orm.review_round,
            review_duration_minutes=orm.review_duration_minutes,
            status=orm.status,
            created_at=orm.created_at,
            submitted_at=orm.submitted_at,
            finalised_at=orm.finalised_at,
        )


# ---------------------------------------------------------------------------
# CalibrationBatch Repository
# ---------------------------------------------------------------------------

class CalibrationBatchRepository:
    """Repository for CalibrationBatch CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, batch: CalibrationBatch) -> CalibrationBatchORM:
        try:
            batch_uuid = uuid.UUID(batch.batch_id)
        except ValueError:
            batch_uuid = uuid.uuid4()

        meta_dict = batch.metadata.to_dict() if batch.metadata else {}
        agreement_dicts = [a.to_dict() for a in batch.agreement_records]

        existing = await self._session.get(CalibrationBatchORM, batch_uuid)
        if existing:
            existing.batch_name = batch.batch_name
            existing.metadata_json = meta_dict
            existing.dataset_ids = batch.dataset_ids
            existing.reviewed_dataset_count = batch.reviewed_dataset_count
            existing.agreement_records = agreement_dicts
            existing.recommended_adjustments = batch.recommended_adjustments
            existing.policy_version_before = batch.policy_version_before
            existing.policy_version_after = batch.policy_version_after
            existing.adjustment_applied = batch.adjustment_applied
            existing.total_discrepancies = batch.total_discrepancies
            existing.constructs_with_discrepancy = batch.constructs_with_discrepancy
            existing.mean_absolute_delta_per_construct = batch.mean_absolute_delta_per_construct
            existing.status = batch.status
            existing.completed_at = batch.completed_at
            await self._session.flush()
            return existing
        else:
            orm = CalibrationBatchORM(
                id=batch_uuid,
                batch_name=batch.batch_name,
                metadata_json=meta_dict,
                dataset_ids=batch.dataset_ids,
                reviewed_dataset_count=batch.reviewed_dataset_count,
                agreement_records=agreement_dicts,
                recommended_adjustments=batch.recommended_adjustments,
                policy_version_before=batch.policy_version_before,
                policy_version_after=batch.policy_version_after,
                adjustment_applied=batch.adjustment_applied,
                total_discrepancies=batch.total_discrepancies,
                constructs_with_discrepancy=batch.constructs_with_discrepancy,
                mean_absolute_delta_per_construct=batch.mean_absolute_delta_per_construct,
                status=batch.status,
                completed_at=batch.completed_at,
            )
            self._session.add(orm)
            await self._session.flush()
            return orm

    async def get_by_id(self, batch_id: str) -> Optional[CalibrationBatch]:
        try:
            uid = uuid.UUID(batch_id)
        except ValueError:
            return None
        orm = await self._session.get(CalibrationBatchORM, uid)
        if not orm or orm.is_deleted:
            return None
        return self._to_entity(orm)

    async def list_all(self, status: Optional[str] = None) -> List[CalibrationBatch]:
        q = select(CalibrationBatchORM).where(CalibrationBatchORM.is_deleted == False)
        if status:
            q = q.where(CalibrationBatchORM.status == status)
        q = q.order_by(CalibrationBatchORM.created_at.desc())
        result = await self._session.execute(q)
        return [self._to_entity(r) for r in result.scalars().all()]

    async def count_open(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(CalibrationBatchORM).where(
                CalibrationBatchORM.status.in_(["OPEN", "IN_PROGRESS"]),
                CalibrationBatchORM.is_deleted == False,
            )
        )
        return result.scalar_one()

    async def count_completed(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(CalibrationBatchORM).where(
                CalibrationBatchORM.status == "COMPLETED",
                CalibrationBatchORM.is_deleted == False,
            )
        )
        return result.scalar_one()

    def _to_entity(self, orm: CalibrationBatchORM) -> CalibrationBatch:
        meta_dict = orm.metadata_json or {}
        metadata = None
        if meta_dict.get("target_policy_version"):
            try:
                metadata = CalibrationMetadata(
                    target_policy_version=meta_dict["target_policy_version"],
                    calibration_round=meta_dict.get("calibration_round", 1),
                    initiated_by=meta_dict.get("initiated_by", "unknown"),
                    rationale=meta_dict.get("rationale", ""),
                    notes=meta_dict.get("notes"),
                )
            except (ValueError, KeyError):
                metadata = None

        agreement_records = [
            AgreementMetrics(
                ai_construct_scores=a.get("ai_construct_scores", {}),
                expert_construct_scores=a.get("expert_construct_scores", {}),
                reviewer_id=a.get("reviewer_id", "unknown"),
                review_round=a.get("review_round", 1),
                score_deltas=a.get("score_deltas", {}),
                discrepant_constructs=a.get("discrepant_constructs", []),
                agreement_flag=a.get("agreement_flag", "PENDING"),
                notes=a.get("notes"),
            )
            for a in (orm.agreement_records or [])
        ]

        batch = CalibrationBatch(
            batch_id=str(orm.id),
            batch_name=orm.batch_name,
            metadata=metadata,
            dataset_ids=orm.dataset_ids,
            reviewed_dataset_count=orm.reviewed_dataset_count,
            agreement_records=agreement_records,
            recommended_adjustments=orm.recommended_adjustments,
            policy_version_before=orm.policy_version_before,
            policy_version_after=orm.policy_version_after,
            adjustment_applied=orm.adjustment_applied,
            total_discrepancies=orm.total_discrepancies,
            constructs_with_discrepancy=orm.constructs_with_discrepancy,
            mean_absolute_delta_per_construct=orm.mean_absolute_delta_per_construct,
            status=orm.status,
            created_at=orm.created_at,
            completed_at=orm.completed_at,
        )
        return batch


# ---------------------------------------------------------------------------
# ResearchExport Repository
# ---------------------------------------------------------------------------

class ResearchExportRepository:
    """Repository for ResearchExport CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, export: ResearchExport) -> ResearchExportORM:
        try:
            export_uuid = uuid.UUID(export.export_id)
        except ValueError:
            export_uuid = uuid.uuid4()

        existing = await self._session.get(ResearchExportORM, export_uuid)
        if existing:
            existing.status = export.status
            existing.file_path = export.file_path
            existing.file_size_bytes = export.file_size_bytes
            existing.record_count = export.record_count
            existing.checksum_sha256 = export.checksum_sha256
            existing.error_message = export.error_message
            existing.completed_at = export.completed_at
            await self._session.flush()
            return existing
        else:
            orm = ResearchExportORM(
                id=export_uuid,
                export_name=export.export_name,
                dataset_ids=export.dataset_ids,
                calibration_batch_id=export.calibration_batch_id,
                record_count=export.record_count,
                export_format=export.export_format,
                include_evidence=export.include_evidence,
                include_transcripts=export.include_transcripts,
                include_expert_reviews=export.include_expert_reviews,
                include_construct_mappings=export.include_construct_mappings,
                file_path=export.file_path,
                file_size_bytes=export.file_size_bytes,
                checksum_sha256=export.checksum_sha256,
                requested_by=export.requested_by,
                export_metadata=export.export_metadata,
                status=export.status,
                error_message=export.error_message,
                completed_at=export.completed_at,
            )
            self._session.add(orm)
            await self._session.flush()
            return orm

    async def get_by_id(self, export_id: str) -> Optional[ResearchExport]:
        try:
            uid = uuid.UUID(export_id)
        except ValueError:
            return None
        orm = await self._session.get(ResearchExportORM, uid)
        if not orm or orm.is_deleted:
            return None
        return self._to_entity(orm)

    async def list_all(self, limit: int = 20) -> List[ResearchExport]:
        result = await self._session.execute(
            select(ResearchExportORM)
            .where(ResearchExportORM.is_deleted == False)
            .order_by(ResearchExportORM.created_at.desc())
            .limit(limit)
        )
        return [self._to_entity(r) for r in result.scalars().all()]

    async def count(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(ResearchExportORM).where(
                ResearchExportORM.is_deleted == False
            )
        )
        return result.scalar_one()

    async def count_by_format(self) -> Dict[str, int]:
        from sqlalchemy import case
        result = await self._session.execute(
            select(ResearchExportORM.export_format, func.count())
            .where(ResearchExportORM.is_deleted == False)
            .group_by(ResearchExportORM.export_format)
        )
        return {row[0]: row[1] for row in result.all()}

    def _to_entity(self, orm: ResearchExportORM) -> ResearchExport:
        return ResearchExport(
            export_id=str(orm.id),
            export_name=orm.export_name,
            dataset_ids=orm.dataset_ids,
            calibration_batch_id=orm.calibration_batch_id,
            record_count=orm.record_count,
            export_format=orm.export_format,
            include_evidence=orm.include_evidence,
            include_transcripts=orm.include_transcripts,
            include_expert_reviews=orm.include_expert_reviews,
            include_construct_mappings=orm.include_construct_mappings,
            file_path=orm.file_path,
            file_size_bytes=orm.file_size_bytes,
            checksum_sha256=orm.checksum_sha256,
            requested_by=orm.requested_by,
            export_metadata=orm.export_metadata,
            status=orm.status,
            error_message=orm.error_message,
            created_at=orm.created_at,
            completed_at=orm.completed_at,
        )
