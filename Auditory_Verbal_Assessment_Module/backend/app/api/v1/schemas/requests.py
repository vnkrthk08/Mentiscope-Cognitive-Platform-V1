from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AssessmentCreateRequest(BaseModel):
    name: str = Field(
        ...,
        description="Name of the assessment",
        json_schema_extra={"example": "Cognitive Priority Assessment v1"},
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the assessment",
        json_schema_extra={"example": "Evaluates rapid decision making, stress tolerance, and listening retention."},
    )


class SessionCreateRequest(BaseModel):
    candidate_id: str = Field(
        ...,
        description="Unique identifier of the candidate",
        json_schema_extra={"example": "CAND-9872"},
    )
    scenario_id: str = Field(
        ...,
        description="Identifier of the scenario config definition",
        json_schema_extra={"example": "SCEN-001"},
    )


class ListeningSubmitRequest(BaseModel):
    question_id: str = Field(
        ...,
        description="Unique identifier of the listening question",
        json_schema_extra={"example": "LQ-1"},
    )
    selected_option_index: int = Field(
        ...,
        ge=0,
        description="Zero-based index of the chosen multiple-choice option",
        json_schema_extra={"example": 2},
    )
    response_time_ms: int = Field(
        default=1500,
        ge=0,
        description="Response execution latency in milliseconds",
        json_schema_extra={"example": 1420},
    )


class SpeakingUploadRequest(BaseModel):
    prompt_id: str = Field(
        ...,
        description="Unique identifier of the speaking prompt item",
        json_schema_extra={"example": "SP-1"},
    )
    duration_seconds: float = Field(
        ...,
        gt=0.0,
        description="Calculated duration of candidate voice response in seconds",
        json_schema_extra={"example": 45.5},
    )
    audio_file_url: str = Field(
        ...,
        description="Absolute storage URL to voice recording asset",
        json_schema_extra={"example": "https://storage.googleapis.com/mentiscope-recordings/session_sp1.wav"},
    )
    transcript_text: Optional[str] = Field(
        None,
        description="Candidate speech transcription text (optional/fallback)",
        json_schema_extra={"example": "Yes, I will initiate emergency containment procedure instantly."},
    )


class SpeakingResponseItem(BaseModel):
    transcript_text: str = Field(default="", description="Candidate spoken transcript")
    duration_seconds: Optional[float] = Field(default=None, description="Recording duration in seconds")
    audio_file_url: Optional[str] = Field(default=None, description="Audio storage URL")
    words_per_second: Optional[float] = Field(default=None, description="Calculated speaking rate")
    pause_ratio: Optional[float] = Field(default=None, description="Acoustic silence/pause ratio")


class SpeakingScoreRequest(BaseModel):
    responses: Optional[Dict[str, SpeakingResponseItem]] = Field(
        default=None,
        description="Optional explicit mapping of question_id (SQ1, SQ2, SQ3) or prompt_id to candidate responses",
    )

