"""
ExpertReview Entity.

Records a psychologist's manual review of a ValidationDataset.
Stores the reviewer's construct scores, comments, and approval
decision. Supports multi-round review workflows.

This entity does NOT compute agreement statistics. AgreementMetrics
is assembled by the CalibrationService after all reviews are collected.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class ExpertReview:
    """
    Domain entity representing one psychologist review of a dataset record.

    Each review is immutable after finalisation (status == SUBMITTED).
    Multiple rounds of review are tracked via review_round.
    """

    # Identity
    review_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dataset_id: str = ""
    reviewer_id: str = ""
    reviewer_name: str = ""
    reviewer_credentials: str = ""

    # Review content
    expert_construct_scores: Dict[str, float] = field(default_factory=dict)
    overall_score: float = 0.0
    comments: str = ""
    strengths: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # Approval decision
    decision: str = "PENDING"   # PENDING | APPROVED | REJECTED | NEEDS_REVISION
    rejection_reason: Optional[str] = None
    revision_notes: Optional[str] = None

    # Annotation metadata
    annotation_tags: List[str] = field(default_factory=list)
    review_round: int = 1
    review_duration_minutes: Optional[float] = None

    # Lifecycle
    status: str = "DRAFT"   # DRAFT | SUBMITTED | FINALISED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    submitted_at: Optional[datetime] = None
    finalised_at: Optional[datetime] = None

    # ---------------------------------------------------------------------------
    # Business rules
    # ---------------------------------------------------------------------------

    def validate(self) -> List[str]:
        """Return validation errors before submission."""
        errors: List[str] = []
        if not self.dataset_id:
            errors.append("dataset_id is required.")
        if not self.reviewer_id:
            errors.append("reviewer_id is required.")
        if not self.expert_construct_scores:
            errors.append("expert_construct_scores must not be empty.")
        if self.overall_score < 0.0 or self.overall_score > 100.0:
            errors.append("overall_score must be between 0.0 and 100.0.")
        for construct, score in self.expert_construct_scores.items():
            if not (0.0 <= score <= 100.0):
                errors.append(f"Score for '{construct}' must be between 0.0 and 100.0.")
        return errors

    def submit(self) -> None:
        """Transition to SUBMITTED; validates required fields first."""
        if self.status != "DRAFT":
            raise ValueError(
                f"ExpertReview can only be submitted from DRAFT state, not '{self.status}'."
            )
        errors = self.validate()
        if errors:
            raise ValueError(f"ExpertReview validation failed: {'; '.join(errors)}")
        self.decision = "APPROVED" if self.decision == "PENDING" else self.decision
        self.status = "SUBMITTED"
        self.submitted_at = datetime.now(timezone.utc)

    def approve(self) -> None:
        """Finalise a submitted review as approved."""
        if self.status != "SUBMITTED":
            raise ValueError("Only SUBMITTED reviews can be approved.")
        self.decision = "APPROVED"
        self.status = "FINALISED"
        self.finalised_at = datetime.now(timezone.utc)

    def reject(self, reason: str) -> None:
        """Finalise a submitted review as rejected with a mandatory reason."""
        if self.status != "SUBMITTED":
            raise ValueError("Only SUBMITTED reviews can be rejected.")
        if not reason:
            raise ValueError("A rejection reason is required.")
        self.decision = "REJECTED"
        self.rejection_reason = reason
        self.status = "FINALISED"
        self.finalised_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "review_id": self.review_id,
            "dataset_id": self.dataset_id,
            "reviewer_id": self.reviewer_id,
            "reviewer_name": self.reviewer_name,
            "reviewer_credentials": self.reviewer_credentials,
            "expert_construct_scores": self.expert_construct_scores,
            "overall_score": self.overall_score,
            "comments": self.comments,
            "strengths": self.strengths,
            "concerns": self.concerns,
            "recommendations": self.recommendations,
            "decision": self.decision,
            "rejection_reason": self.rejection_reason,
            "revision_notes": self.revision_notes,
            "annotation_tags": self.annotation_tags,
            "review_round": self.review_round,
            "review_duration_minutes": self.review_duration_minutes,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "finalised_at": self.finalised_at.isoformat() if self.finalised_at else None,
        }
