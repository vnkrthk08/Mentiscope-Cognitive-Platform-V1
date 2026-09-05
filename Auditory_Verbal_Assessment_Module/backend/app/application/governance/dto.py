"""
MGEP DTO Schemas (Pydantic v2).
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Model Registry DTOs
# ---------------------------------------------------------------------------


class RegisterModelRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Model or component name")
    category: str = Field(
        ...,
        description="Category: SPEECH, PROMPT_TEMPLATE, LLM_MODEL, BEHAVIOR_EXTRACTOR, CONSTRUCT_MAPPING, SCORING_POLICY",
    )
    version: str = Field(..., min_length=1, description="Semantic version string")
    owner: str = Field(..., min_length=1, description="Responsible owner/team")
    description: str = Field("", description="Optional description")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Configuration parameters")


class RegisteredModelResponse(BaseModel):
    model_id: str
    name: str
    category: str
    version: str
    owner: str
    description: str
    checksum: str
    configuration: Dict[str, Any]
    status: str
    created_at: str
    updated_at: str


# ---------------------------------------------------------------------------
# Configuration Snapshot DTOs
# ---------------------------------------------------------------------------


class CreateSnapshotRequest(BaseModel):
    snapshot_name: str = Field(..., min_length=1)
    created_by: str = Field(..., min_length=1)
    speech_model_id: Optional[str] = None
    prompt_template_id: Optional[str] = None
    llm_model_id: Optional[str] = None
    behavior_extractor_id: Optional[str] = None
    construct_policy_id: Optional[str] = None
    scoring_policy_id: Optional[str] = None
    full_config: Dict[str, Any] = Field(default_factory=dict)


class ConfigurationSnapshotResponse(BaseModel):
    snapshot_id: str
    snapshot_name: str
    config_hash: str
    speech_model_id: Optional[str]
    prompt_template_id: Optional[str]
    llm_model_id: Optional[str]
    behavior_extractor_id: Optional[str]
    construct_policy_id: Optional[str]
    scoring_policy_id: Optional[str]
    full_config: Dict[str, Any]
    created_by: str
    created_at: str


# ---------------------------------------------------------------------------
# Experiment DTOs
# ---------------------------------------------------------------------------


class CreateExperimentRequest(BaseModel):
    title: str = Field(..., min_length=1)
    owner: str = Field(..., min_length=1)
    baseline_snapshot_id: str = Field(..., min_length=1)
    candidate_snapshot_id: str = Field(..., min_length=1)
    description: str = ""
    dataset_sample_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExperimentRunResponse(BaseModel):
    run_id: str
    experiment_id: str
    run_type: str
    snapshot_id: str
    dataset_id: str
    transcript_output: str
    behavior_evidence_output: Dict[str, Any]
    construct_evaluation_output: Dict[str, Any]
    assessment_scores_output: Dict[str, Any]
    confidence_values: Dict[str, float]
    processing_latency_ms: float
    token_usage: Dict[str, int]
    estimated_cost_usd: float
    status: str
    executed_at: str


class ExperimentResponse(BaseModel):
    experiment_id: str
    title: str
    description: str
    owner: str
    status: str
    baseline_snapshot_id: str
    candidate_snapshot_id: str
    dataset_sample_ids: List[str]
    metadata: Dict[str, Any]
    created_at: str
    completed_at: Optional[str]
    runs: List[ExperimentRunResponse] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Comparison DTOs
# ---------------------------------------------------------------------------


class CompareRunsRequest(BaseModel):
    experiment_id: str = Field(..., min_length=1)
    baseline_run_id: Optional[str] = None
    candidate_run_id: Optional[str] = None


class ComparisonReportResponse(BaseModel):
    report_id: str
    experiment_id: str
    baseline_run_id: str
    candidate_run_id: str
    prompt_diff_summary: Dict[str, Any]
    evidence_diff_summary: Dict[str, Any]
    evaluation_diff_summary: Dict[str, Any]
    score_deltas: Dict[str, float]
    latency_delta_ms: float
    cost_delta_usd: float
    overall_recommendation: str
    generated_at: str
