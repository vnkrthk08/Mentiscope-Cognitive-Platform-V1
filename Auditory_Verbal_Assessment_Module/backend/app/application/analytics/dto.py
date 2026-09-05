"""
RAIP DTO Schemas (Pydantic v2).
"""
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TrendPointResponse(BaseModel):
    date: str
    count: int
    completion_rate: float


class AssessmentAnalyticsResponse(BaseModel):
    total_assessments: int
    completed_assessments: int
    in_progress_assessments: int
    overall_completion_rate: float
    by_scenario: Dict[str, int]
    trend_series: List[TrendPointResponse]


class FrameworkMetricsResponse(BaseModel):
    framework_name: str
    average_score: float
    average_confidence: float
    coverage_rate: float
    total_evaluations: int
    score_distribution: Dict[str, int]


class FrameworkAnalyticsResponse(BaseModel):
    chc: FrameworkMetricsResponse
    riasec: FrameworkMetricsResponse
    personality: FrameworkMetricsResponse
    emotional_regulation: FrameworkMetricsResponse
    all_frameworks: List[FrameworkMetricsResponse]


class ObservationFrequencyResponse(BaseModel):
    construct_name: str
    count: int
    avg_confidence: float


class EvidenceAnalyticsResponse(BaseModel):
    total_evidence_count: int
    average_quality_score: float
    evidence_utilization_rate: float
    top_observation_frequencies: List[ObservationFrequencyResponse]
    quality_by_evidence_type: Dict[str, float]


class ReviewerWorkloadResponse(BaseModel):
    reviewer_id: str
    reviewer_name: str
    completed_reviews: int
    approved_reviews: int
    rejected_reviews: int


class ResearchAnalyticsResponse(BaseModel):
    total_validation_datasets: int
    ready_datasets: int
    total_expert_reviews: int
    approved_reviews: int
    total_calibration_batches: int
    completed_calibration_batches: int
    total_exports: int
    exports_by_format: Dict[str, int]
    reviewer_workloads: List[ReviewerWorkloadResponse]


class PlatformAnalyticsResponse(BaseModel):
    speech_provider_usage: Dict[str, int]
    prompt_provider_usage: Dict[str, int]
    avg_speech_latency_ms: float
    avg_prompt_latency_ms: float
    avg_pipeline_latency_ms: float
    pipeline_completion_rate: float
    overall_failure_rate: float
    error_count_by_type: Dict[str, int]


class DashboardSnapshotResponse(BaseModel):
    snapshot_id: str
    time_window: str
    generated_at: datetime
    assessments: AssessmentAnalyticsResponse
    frameworks: FrameworkAnalyticsResponse
    evidence: EvidenceAnalyticsResponse
    research: ResearchAnalyticsResponse
    platform: PlatformAnalyticsResponse
