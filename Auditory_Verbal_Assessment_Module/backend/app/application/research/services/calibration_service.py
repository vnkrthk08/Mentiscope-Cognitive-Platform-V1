"""
CalibrationService — Application Service.

Manages calibration batch lifecycle: creation, dataset association,
discrepancy aggregation, recommendation recording, and completion.

This service NEVER auto-applies score adjustments.
All recommendations are advisory only.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.domain.research.entities.calibration_batch import CalibrationBatch
from app.domain.research.entities.expert_review import ExpertReview
from app.domain.research.value_objects.calibration_metadata import CalibrationMetadata
from app.domain.research.value_objects.agreement_metrics import AgreementMetrics
from app.application.research.events.research_events import (
    CalibrationBatchCreated,
    CalibrationBatchCompleted,
    ExpertReviewSubmitted,
)


class CalibrationService:
    """
    Application service managing calibration batch workflows.

    Coordinates expert review submission, agreement metric assembly,
    and calibration batch lifecycle transitions.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def create_batch(
        self,
        batch_name: str,
        target_policy_version: str,
        calibration_round: int,
        initiated_by: str,
        rationale: str,
        dataset_ids: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> CalibrationBatch:
        """Create a new calibration batch entity."""
        metadata = CalibrationMetadata(
            target_policy_version=target_policy_version,
            calibration_round=calibration_round,
            initiated_by=initiated_by,
            rationale=rationale,
            notes=notes,
        )
        batch = CalibrationBatch(
            batch_id=str(uuid.uuid4()),
            batch_name=batch_name,
            metadata=metadata,
            dataset_ids=list(dataset_ids or []),
            policy_version_before=target_policy_version,
        )
        logger.info(
            f"[PVCSF CalibrationService] Created calibration batch: {batch.batch_id} (round {calibration_round})"
        )
        return batch

    def process_expert_review(
        self,
        batch: CalibrationBatch,
        review: ExpertReview,
        ai_scores: Dict[str, float],
    ) -> AgreementMetrics:
        """
        Submit an expert review, compute raw agreement metrics,
        and attach them to the calibration batch.
        """
        # Submit the review (transitions DRAFT → SUBMITTED)
        review.submit()
        if review.approved if hasattr(review, 'approved') else (review.decision == "APPROVED"):
            review.approve()

        # Build AgreementMetrics from AI vs expert score comparison
        deltas = {
            construct: round(ai_scores.get(construct, 0.0)
                             - review.expert_construct_scores.get(construct, 0.0), 4)
            for construct in set(ai_scores) | set(review.expert_construct_scores)
        }
        discrepant = [c for c, d in deltas.items() if abs(d) > 5.0]
        flag = (
            "AGREEMENT" if not discrepant
            else "DISCREPANT" if len(discrepant) > len(ai_scores) // 2
            else "PARTIAL"
        )

        metrics = AgreementMetrics(
            ai_construct_scores=ai_scores,
            expert_construct_scores=review.expert_construct_scores,
            reviewer_id=review.reviewer_id,
            review_round=review.review_round,
            score_deltas=deltas,
            discrepant_constructs=discrepant,
            agreement_flag=flag,
            notes=review.comments,
        )

        batch.record_agreement(metrics)
        if batch.status == "OPEN":
            batch.status = "IN_PROGRESS"

        logger.info(
            f"[PVCSF CalibrationService] Expert review processed: {review.review_id} (flag: {flag}, discrepant: {len(discrepant)})"
        )
        return metrics

    def add_recommendation(
        self,
        batch: CalibrationBatch,
        framework: str,
        construct: str,
        delta: float,
        justification: str,
    ) -> None:
        """Record a score adjustment recommendation (advisory only)."""
        batch.add_recommendation(framework, construct, delta)
        logger.info(
            f"[PVCSF CalibrationService] Recommendation recorded: batch {batch.batch_id}, framework {framework}, construct {construct}, delta {delta}, justification {justification}"
        )

    def complete_batch(self, batch: CalibrationBatch) -> CalibrationBatchCompleted:
        """Finalize the calibration batch and compute summary statistics."""
        batch.complete()
        event = CalibrationBatchCompleted(
            batch_id=batch.batch_id,
            total_discrepancies=batch.total_discrepancies,
            reviewed_count=batch.reviewed_dataset_count,
            status=batch.status,
        )
        logger.info(
            f"[PVCSF CalibrationService] Calibration batch completed: {batch.batch_id} (discrepancies: {batch.total_discrepancies})"
        )
        return event

    def build_expert_review(
        self,
        dataset_id: str,
        reviewer_id: str,
        reviewer_name: str,
        reviewer_credentials: str,
        expert_scores: Dict[str, float],
        overall_score: float,
        comments: str,
        strengths: List[str],
        concerns: List[str],
        recommendations: List[str],
        approved: bool,
        rejection_reason: Optional[str] = None,
        annotation_tags: Optional[List[str]] = None,
        review_round: int = 1,
        review_duration_minutes: Optional[float] = None,
    ) -> ExpertReview:
        """Factory method to construct an ExpertReview entity."""
        review = ExpertReview(
            review_id=str(uuid.uuid4()),
            dataset_id=dataset_id,
            reviewer_id=reviewer_id,
            reviewer_name=reviewer_name,
            reviewer_credentials=reviewer_credentials,
            expert_construct_scores=expert_scores,
            overall_score=overall_score,
            comments=comments,
            strengths=strengths,
            concerns=concerns,
            recommendations=recommendations,
            decision="APPROVED" if approved else "REJECTED",
            rejection_reason=rejection_reason,
            annotation_tags=annotation_tags or [],
            review_round=review_round,
            review_duration_minutes=review_duration_minutes,
        )
        return review
