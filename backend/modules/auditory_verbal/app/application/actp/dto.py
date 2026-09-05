"""
ACTP DTO Schemas (Pydantic v2).
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Audit Session & Event DTOs
# ---------------------------------------------------------------------------


class AuditEventResponse(BaseModel):
    event_id: str
    session_id: str
    assessment_id: str
    event_type: str
    step_order: int
    stage_name: str
    payload: Dict[str, Any]
    invocation: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    timestamp: str


class AuditSessionResponse(BaseModel):
    session_id: str
    assessment_id: str
    candidate_id: str
    scenario_id: str
    session_status: str
    total_events: int
    metadata: Optional[Dict[str, Any]]
    events: List[AuditEventResponse] = Field(default_factory=list)
    started_at: str
    completed_at: Optional[str]


class AuditSessionListResponse(BaseModel):
    sessions: List[AuditSessionResponse]
    total: int
    page: int
    page_size: int


# ---------------------------------------------------------------------------
# Timeline DTOs
# ---------------------------------------------------------------------------


class TimelineStepResponse(BaseModel):
    step_order: int
    stage_name: str
    event_type: str
    title: str
    description: str
    status: str
    timestamp: str
    details: Dict[str, Any]


class TimelineResponse(BaseModel):
    assessment_id: str
    candidate_id: str
    scenario_id: str
    total_steps: int
    steps: List[TimelineStepResponse]
    generated_at: str


# ---------------------------------------------------------------------------
# Trace Graph DTOs
# ---------------------------------------------------------------------------


class TraceNodeResponse(BaseModel):
    node_id: str
    node_type: str
    label: str
    stage: str
    status: str
    details: Dict[str, Any]
    timestamp: str


class TraceEdgeResponse(BaseModel):
    edge_id: str
    source_node_id: str
    target_node_id: str
    relation_type: str
    description: str


class TraceGraphResponse(BaseModel):
    assessment_id: str
    node_count: int
    edge_count: int
    nodes: List[TraceNodeResponse]
    edges: List[TraceEdgeResponse]
    generated_at: str


# ---------------------------------------------------------------------------
# Decision Record DTOs
# ---------------------------------------------------------------------------


class ScoreExplanationResponse(BaseModel):
    framework_name: str
    construct_name: str
    raw_score: float
    normalized_score: float
    weight: float
    scoring_policy_id: str
    confidence: float


class EvidenceReferenceResponse(BaseModel):
    evidence_id: str
    construct_name: str
    verbatim_quote: str
    behavioral_indicator: str
    confidence: float
    evidence_type: str


class DecisionRecordResponse(BaseModel):
    record_id: str
    decision_id: str
    assessment_id: str
    decision_type: str
    input_data: Dict[str, Any]
    output_decision: Dict[str, Any]
    score_explanations: List[ScoreExplanationResponse]
    evidence_references: List[EvidenceReferenceResponse]
    pipeline_invocation: Optional[Dict[str, Any]]
    reproducible_hash: str
    recorded_at: str
