from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from app.domain.events.base_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class AssessmentStarted(DomainEvent):
    session_id: str
    candidate_id: str
    scenario_id: str


@dataclass(frozen=True, kw_only=True)
class StageEntered(DomainEvent):
    session_id: str
    previous_stage: str
    current_stage: str


@dataclass(frozen=True, kw_only=True)
class StageCompleted(DomainEvent):
    session_id: str
    completed_stage: str


@dataclass(frozen=True, kw_only=True)
class ScenarioLoaded(DomainEvent):
    session_id: str
    scenario_id: str
    title: str
    version: str


@dataclass(frozen=True, kw_only=True)
class ListeningStarted(DomainEvent):
    session_id: str
    total_questions: int


@dataclass(frozen=True, kw_only=True)
class ListeningCompleted(DomainEvent):
    session_id: str
    questions_count: int
    correct_answers_count: int


@dataclass(frozen=True, kw_only=True)
class SpeakingStarted(DomainEvent):
    session_id: str
    total_prompts: int


@dataclass(frozen=True, kw_only=True)
class SpeakingCompleted(DomainEvent):
    session_id: str
    prompt_id: str
    audio_asset_url: str


@dataclass(frozen=True, kw_only=True)
class AudioUploaded(DomainEvent):
    session_id: str
    prompt_id: str
    file_path: str
    file_size_bytes: int


@dataclass(frozen=True, kw_only=True)
class TranscriptGenerated(DomainEvent):
    session_id: str
    prompt_id: str
    transcript_text: str


@dataclass(frozen=True, kw_only=True)
class FollowUpStarted(DomainEvent):
    session_id: str
    parent_prompt_id: str


@dataclass(frozen=True, kw_only=True)
class FollowUpGenerated(DomainEvent):
    session_id: str
    followup_id: str
    target_construct: str


@dataclass(frozen=True, kw_only=True)
class EvidenceStarted(DomainEvent):
    session_id: str


@dataclass(frozen=True, kw_only=True)
class EvidenceExtracted(DomainEvent):
    session_id: str
    prompt_id: str
    evidence_items_count: int


@dataclass(frozen=True, kw_only=True)
class EvidenceCompleted(DomainEvent):
    session_id: str
    total_evidence_count: int


@dataclass(frozen=True, kw_only=True)
class ScoringStarted(DomainEvent):
    session_id: str


@dataclass(frozen=True, kw_only=True)
class ConstructEvaluated(DomainEvent):
    session_id: str
    construct_id: str
    score: float


@dataclass(frozen=True, kw_only=True)
class ScoringCompleted(DomainEvent):
    session_id: str
    overall_cognitive_index: float


@dataclass(frozen=True, kw_only=True)
class AssessmentCompleted(DomainEvent):
    session_id: str
    candidate_id: str
    total_duration_seconds: float


@dataclass(frozen=True, kw_only=True)
class AssessmentPaused(DomainEvent):
    session_id: str
    paused_at_stage: str
    reason: str


@dataclass(frozen=True, kw_only=True)
class AssessmentRecovered(DomainEvent):
    session_id: str
    restored_stage: str
