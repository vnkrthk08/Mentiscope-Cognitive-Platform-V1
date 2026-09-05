from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProblemDetails(BaseModel):
    """RFC7807 compliant Problem Details error payload."""

    type: str = Field(..., description="URI reference identifying the error type")
    title: str = Field(..., description="Short, human-readable summary of the error type")
    status: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Human-readable explanation specific to this occurrence")
    instance: Optional[str] = Field(None, description="URI reference that identifies the specific occurrence")
    invalid_params: Optional[List[Dict[str, Any]]] = Field(None, description="Detailed validation parameters validation errors list")


class AssessmentResponse(BaseModel):
    id: str = Field(..., description="Unique assessment record identifier")
    name: str = Field(..., description="Assessment name")
    description: Optional[str] = Field(None, description="Detailed description")
    version: int = Field(..., description="Optimistic locking version tracker")
    created_at: datetime = Field(..., description="Timestamp of record creation")


class SessionResponse(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    candidate_id: str = Field(..., description="Candidate identifier")
    scenario_id: str = Field(..., description="Scenario identifier")
    status: str = Field(..., description="Operational status of the session")
    current_stage: str = Field(..., description="FSM assessment stage location")
    completed_stages: List[str] = Field(..., description="List of stages completed successfully")
    metadata: Dict[str, Any] = Field(..., description="Session state metadata context")


class ListeningQuestionResponse(BaseModel):
    question_id: str = Field(..., description="Listening Question ID")
    prompt: str = Field(..., description="Question prompt text")
    options: List[str] = Field(..., description="Multiple choice answer options")
    correct_option_index: int = Field(..., description="Zero-based index of correct option")
    target_construct: str = Field(..., description="Cognitive/Psychological construct evaluated")
    difficulty: str = Field(..., description="Difficulty level classification")
    points: int = Field(..., description="Points awarded for correct response")
    max_replays: int = Field(..., description="Max replays permitted")


class BehaviouralIndicatorResponse(BaseModel):
    indicator_id: str = Field(..., description="Indicator ID, e.g. SQ1_IND_1")
    name: str = Field(..., description="Indicator description")
    weight: float = Field(..., description="Psychometric weight")
    scale: str = Field("0-4", description="Measurement scale")
    anchors: Dict[str, str] = Field(default_factory=dict, description="Behavioral anchors 0-4")


class SpeakingPromptResponse(BaseModel):
    question_id: str = Field("SQ1", description="Canonical Question ID: SQ1, SQ2, SQ3")
    prompt_id: str = Field(..., description="Speaking prompt ID")
    stage: str = Field("STAGE_1_DECISION", description="Canonical Stage: STAGE_1_DECISION, STAGE_2_CHALLENGE, STAGE_3_REFLECTIVE")
    title: str = Field(..., description="Task title")
    instructions: str = Field(..., description="Candidate task instructions text")
    objective: str = Field("", description="Psychometric evaluation objective")
    primary_constructs: List[str] = Field(default_factory=list, description="Primary evaluated constructs")
    secondary_constructs: List[str] = Field(default_factory=list, description="Secondary evaluated constructs")
    behavioural_indicators: List[BehaviouralIndicatorResponse] = Field(default_factory=list, description="Observable behavioural indicators with anchors")
    max_seconds: float = Field(..., description="Maximum duration limit in seconds")
    max_indicator_weighted_score: float = Field(18.4, description="Maximum indicator weighted score")
    target_constructs: List[str] = Field(default_factory=list, description="Combined target constructs (backward compatibility)")
    followup_eligible: bool = Field(..., description="Eligible for adaptive follow-up")



class TranscriptResponse(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    prompt_id: str = Field(..., description="Speaking prompt identifier")
    transcript_text: str = Field(..., description="Response transcription text")
    confidence_score: float = Field(..., description="AI confidence score")
    is_final: bool = Field(..., description="Finalized status indicator")


class ReportResponse(BaseModel):
    report_id: str = Field(..., description="Report identifier")
    session_id: str = Field(..., description="Session identifier")
    candidate_id: str = Field(..., description="Candidate identifier")
    scenario_id: str = Field(..., description="Scenario identifier")
    overall_cognitive_index: float = Field(..., description="Calculated overall cognitive competency score")
    listening_metrics: List[Dict[str, Any]] = Field(..., description="Listening stage evaluation metrics")
    speaking_metrics: List[Dict[str, Any]] = Field(..., description="Speaking stage evaluation metrics")
    construct_scores: Dict[str, float] = Field(..., description="Scores for evaluated constructs")
    evidence_summary: List[Dict[str, Any]] = Field(..., description="List of behavioral evidence extracted")
    recommendations: List[str] = Field(..., description="System recommendations")
    generated_at: datetime = Field(..., description="Timestamp of report generation")
