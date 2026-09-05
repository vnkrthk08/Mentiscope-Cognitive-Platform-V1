from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.domain.entities.scenario import Scenario


class DTOListeningQuestion(BaseModel):
    question_id: str = Field(..., description="Listening Question ID")
    prompt: str = Field(..., description="Question prompt text")
    options: List[str] = Field(..., description="Multiple choice options")
    correct_option_index: int = Field(..., description="Zero-based index of correct option")
    target_construct: str = Field(..., description="Construct evaluated")
    difficulty: str = Field(..., description="Difficulty level")
    points: int = Field(10, description="Points awarded")
    max_replays: int = Field(2, description="Max audio replays permitted")


class DTOBehaviouralIndicator(BaseModel):
    indicator_id: str = Field(..., description="Indicator ID, e.g. SQ1_IND_1")
    name: str = Field(..., description="Indicator description/name")
    weight: float = Field(..., description="Psychometric weight")
    scale: str = Field("0-4", description="Measurement scale")
    anchors: Dict[str, str] = Field(default_factory=dict, description="Behavioral anchors for scores 0-4")


class DTOSpeakingPrompt(BaseModel):
    question_id: str = Field("SQ1", description="Canonical Question ID: SQ1, SQ2, SQ3")
    prompt_id: str = Field(..., description="Instance prompt ID")
    stage: str = Field("STAGE_1_DECISION", description="Stage: STAGE_1_DECISION, STAGE_2_CHALLENGE, STAGE_3_REFLECTIVE")
    title: str = Field(..., description="Prompt title")
    instructions: str = Field(..., description="Task instruction details")
    objective: str = Field("", description="Psychometric objective")
    primary_constructs: List[str] = Field(default_factory=list, description="Primary construct(s)")
    secondary_constructs: List[str] = Field(default_factory=list, description="Secondary construct(s)")
    behavioural_indicators: List[DTOBehaviouralIndicator] = Field(default_factory=list, description="Behavioral indicators with anchors")
    max_seconds: float = Field(120.0, description="Max speaking duration in seconds")
    max_indicator_weighted_score: float = Field(18.4, description="Max indicator weighted score")
    target_constructs: List[str] = Field(default_factory=list, description="Combined target constructs (backward compatibility)")
    followup_eligible: bool = Field(True, description="Eligible for follow-up")


class DTOFollowUpDefinition(BaseModel):
    id: str = Field(..., description="Follow-up question ID")
    parent_prompt_id: str = Field(..., description="Parent prompt ID")
    prompt_text: str = Field(..., description="Follow-up prompt text")
    target_construct: str = Field(..., description="Construct evaluated")
    priority: int = Field(1, description="Triggers priority queue")
    trigger_conditions: Dict[str, Any] = Field(default_factory=dict, description="Adaptive triggers conditions")
    expected_evidence_pattern: str = Field("", description="Expected answer pattern regex")
    max_seconds: float = Field(..., description="Max response seconds")


class ScenarioDTO(BaseModel):
    """Data Transport Object representing a scenario returned to the frontend."""

    scenario_id: str = Field(..., description="Authoritative scenario ID")
    title: str = Field(..., description="Scenario Title")
    narrative: str = Field(..., description="Listening narrative text")
    difficulty: str = Field(..., description="Unified difficulty level")
    audio_asset: Dict[str, Any] = Field(..., description="Audio file reference URL and parameters")
    listening_questions: List[DTOListeningQuestion] = Field(..., description="MCQs")
    speaking_prompts: List[DTOSpeakingPrompt] = Field(..., description="Speaking tasks")
    version: str = Field("1.0.0", description="Version of the scenario schema")
    construct_mappings: List[str] = Field(..., description="All cognitive constructs mapped in this scenario")
    metadata: Dict[str, Any] = Field(..., description="Generated scenario planning metadata")
    follow_ups: List[DTOFollowUpDefinition] = Field(default_factory=list, description="Follow-up triggers")

    @classmethod
    def from_domain(cls, domain: Scenario) -> "ScenarioDTO":
        """Build DTO from rich domain entity."""
        return cls(
            scenario_id=domain.scenario_id,
            title=domain.title,
            narrative=domain.narrative,
            difficulty=domain.difficulty.value,
            audio_asset={
                "file_path": domain.audio_asset.url,
                "url": domain.audio_asset.url,
                "duration_seconds": domain.audio_asset.duration_seconds,
                "format": domain.audio_asset.format,
            },
            listening_questions=[
                DTOListeningQuestion(
                    question_id=q.question_id,
                    prompt=q.prompt,
                    options=q.options,
                    correct_option_index=q.correct_option_index,
                    target_construct=q.target_construct.value,
                    difficulty=q.difficulty.value,
                    points=q.points,
                    max_replays=q.max_replays,
                )
                for q in domain.listening_questions
            ],
            speaking_prompts=[
                DTOSpeakingPrompt(
                    question_id=p.question_id,
                    prompt_id=p.prompt_id,
                    stage=p.stage,
                    title=p.title,
                    instructions=p.instructions,
                    objective=p.objective,
                    primary_constructs=[c.value for c in p.primary_constructs],
                    secondary_constructs=[c.value for c in p.secondary_constructs],
                    behavioural_indicators=[
                        DTOBehaviouralIndicator(
                            indicator_id=ind.indicator_id,
                            name=ind.name,
                            weight=ind.weight,
                            scale=ind.scale,
                            anchors=ind.anchors,
                        )
                        for ind in p.behavioural_indicators
                    ],
                    max_seconds=float(p.time_limit.max_seconds),
                    max_indicator_weighted_score=p.max_indicator_weighted_score,
                    target_constructs=[c.value for c in p.target_constructs],
                    followup_eligible=p.followup_eligible,
                )
                for p in domain.speaking_prompts
            ],
            construct_mappings=[c.value for c in domain.construct_mappings],
            metadata=domain.metadata,
            follow_ups=[
                DTOFollowUpDefinition(
                    id=f.followup_id,
                    parent_prompt_id=f.parent_prompt_id,
                    prompt_text=f.prompt_text,
                    target_construct=f.target_construct.value,
                    priority=f.priority,
                    trigger_conditions=f.trigger_conditions,
                    expected_evidence_pattern=f.expected_evidence_pattern,
                    max_seconds=float(f.time_limit.max_seconds),
                )
                for f in domain.follow_up_definitions
            ],
        )
