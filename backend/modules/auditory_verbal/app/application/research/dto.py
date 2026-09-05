"""
PVCSF Data Transfer Objects.

Pydantic v2 request/response schemas for all PVCSF API endpoints.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Dataset DTOs
# ---------------------------------------------------------------------------

class BuildDatasetRequest(BaseModel):
    """Request to build a ValidationDataset from a completed assessment run."""

    candidate_id: str = Field(..., min_length=1, description="Candidate identifier")
    assessment_id: str = Field(..., min_length=1, description="Assessment definition UUID")
    session_id: str = Field(..., min_length=1, description="Assessment session UUID")
    scenario_id: str = Field(..., min_length=1, description="Scenario identifier")
    pipeline_version: str = Field("1.0.0", description="Pipeline version tag")
    model_version: str = Field("gemini-1.5-pro", description="LLM model version")
    prompt_version: str = Field("1.0.0", description="Prompt template version")
    scoring_policy_version: str = Field("1.0.0", description="Scoring policy version")
    notes: Optional[str] = Field(None, description="Optional researcher notes")


class ValidationDatasetResponse(BaseModel):
    """Response envelope for a ValidationDataset."""

    dataset_id: str
    candidate_id: str
    assessment_id: str
    scenario_id: str
    session_id: str
    transcript_text: str
    transcript_confidence: float
    observation_count: int
    behavior_confidence: float
    frameworks_evaluated: List[str]
    ai_composite_score: float
    score_confidence: float
    ai_framework_scores: Dict[str, float]
    expert_ratings: Dict[str, float]
    reviewer_notes: str
    review_status: str
    dataset_status: str
    pipeline_version: str
    model_version: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DatasetListResponse(BaseModel):
    """Paginated list of ValidationDataset summaries."""

    datasets: List[ValidationDatasetResponse]
    total: int
    page: int
    page_size: int


# ---------------------------------------------------------------------------
# Expert Review DTOs
# ---------------------------------------------------------------------------

class ExpertReviewRequest(BaseModel):
    """Request to submit a psychologist expert review."""

    dataset_id: str = Field(..., description="ValidationDataset to review")
    reviewer_id: str = Field(..., description="Psychologist user ID")
    reviewer_name: str = Field(..., description="Full name for audit trail")
    reviewer_credentials: str = Field("", description="Professional credentials (e.g. PhD, Psychologist)")
    expert_construct_scores: Dict[str, float] = Field(
        ..., description="Manually assigned scores per construct (0-100)"
    )
    overall_score: float = Field(..., ge=0.0, le=100.0)
    comments: str = Field("", description="Qualitative review comments")
    strengths: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    approved: bool = Field(..., description="True = APPROVED, False = REJECTED")
    rejection_reason: Optional[str] = Field(None)
    annotation_tags: List[str] = Field(default_factory=list)
    review_round: int = Field(1, ge=1)
    review_duration_minutes: Optional[float] = None

    @field_validator("expert_construct_scores")
    @classmethod
    def validate_scores(cls, v: Dict[str, float]) -> Dict[str, float]:
        for construct, score in v.items():
            if not (0.0 <= score <= 100.0):
                raise ValueError(f"Score for '{construct}' must be 0-100.")
        return v


class ExpertReviewResponse(BaseModel):
    """Response envelope for an ExpertReview."""

    review_id: str
    dataset_id: str
    reviewer_id: str
    reviewer_name: str
    reviewer_credentials: str
    expert_construct_scores: Dict[str, float]
    overall_score: float
    comments: str
    strengths: List[str]
    concerns: List[str]
    recommendations: List[str]
    decision: str
    rejection_reason: Optional[str]
    annotation_tags: List[str]
    review_round: int
    status: str
    created_at: datetime
    submitted_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Calibration DTOs
# ---------------------------------------------------------------------------

class CreateCalibrationRequest(BaseModel):
    """Request to create a new calibration batch."""

    batch_name: str = Field(..., min_length=1)
    target_policy_version: str = Field(..., description="The scoring policy version being calibrated")
    calibration_round: int = Field(1, ge=1)
    initiated_by: str = Field(..., description="Username or ID of the researcher initiating the batch")
    rationale: str = Field(..., min_length=10, description="Scientific rationale for this calibration round")
    dataset_ids: List[str] = Field(default_factory=list, description="Pre-select datasets to include")
    notes: Optional[str] = None


class AddRecommendationRequest(BaseModel):
    """Request to add a score adjustment recommendation to a calibration batch."""

    framework: str = Field(..., description="e.g. CHC, RIASEC, PERSONALITY")
    construct_name: str = Field(..., description="Construct name within the framework")
    delta: float = Field(..., description="Recommended score adjustment (positive = increase)")
    justification: str = Field(..., min_length=5)


class CalibrationBatchResponse(BaseModel):
    """Response envelope for a CalibrationBatch."""

    batch_id: str
    batch_name: str
    dataset_ids: List[str]
    reviewed_dataset_count: int
    recommended_adjustments: Dict[str, Any]
    policy_version_before: str
    policy_version_after: Optional[str]
    adjustment_applied: bool
    total_discrepancies: int
    constructs_with_discrepancy: List[str]
    mean_absolute_delta_per_construct: Dict[str, float]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    metadata: Optional[Dict[str, Any]]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Export DTOs
# ---------------------------------------------------------------------------

class CreateExportRequest(BaseModel):
    """Request to generate a dataset export."""

    export_name: str = Field(..., min_length=1)
    export_format: str = Field("CSV", pattern="^(CSV|JSON|EXCEL)$")
    dataset_ids: List[str] = Field(default_factory=list, description="Specific datasets; empty = all READY")
    calibration_batch_id: Optional[str] = Field(None, description="Export datasets from a specific batch")
    requested_by: str = Field(..., description="Username of exporting researcher")
    include_evidence: bool = True
    include_transcripts: bool = True
    include_expert_reviews: bool = True
    include_construct_mappings: bool = True


class ExportResponse(BaseModel):
    """Response envelope for a ResearchExport."""

    export_id: str
    export_name: str
    dataset_ids: List[str]
    calibration_batch_id: Optional[str]
    record_count: int
    export_format: str
    file_path: Optional[str]
    file_size_bytes: int
    checksum_sha256: Optional[str]
    requested_by: str
    status: str
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Research metrics summary
# ---------------------------------------------------------------------------

class ResearchMetricsSummary(BaseModel):
    """High-level PVCSF operational metrics for the research dashboard."""

    total_datasets: int
    ready_datasets: int
    exported_datasets: int
    pending_reviews: int
    approved_reviews: int
    open_calibration_batches: int
    completed_calibration_batches: int
    total_exports: int
    export_by_format: Dict[str, int]
    dataset_generation_time_avg_ms: float
    last_export_at: Optional[datetime]
