from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator


class BehavioralEvidenceItem(BaseModel):
    category: str = "General"
    quote: str = ""
    confidence: float = 0.9


class AdaptiveFollowupResponse(BaseModel):
    internal_reasoning: str
    answer_quality: str
    intent: str
    is_relevant: bool
    needs_clarification: bool
    follow_up_question: str
    behavioral_evidence: List[Union[BehavioralEvidenceItem, Dict[str, Any], str]] = Field(default_factory=list)

    @field_validator("behavioral_evidence", mode="before")
    @classmethod
    def normalize_evidence(cls, v):
        if not isinstance(v, list):
            return []
        normalized = []
        for item in v:
            if isinstance(item, str):
                normalized.append({"category": "General", "quote": item, "confidence": 0.9})
            elif isinstance(item, dict):
                cat = item.get("category") or item.get("type") or "General"
                quote = item.get("quote") or item.get("text") or item.get("description") or str(item)
                conf = float(item.get("confidence", 0.9))
                normalized.append({"category": cat, "quote": quote, "confidence": conf})
            else:
                normalized.append(item)
        return normalized


class EvidenceExtractionResponse(BaseModel):
    verbatim_quotes: List[str]
    behavioral_indicators: List[str]
    confidence_score: float


class ConstructEvaluationItem(BaseModel):
    construct: str
    behavioral_summary: str
    evaluation_narrative: str
    confidence: float


class ConstructEvaluationResponse(BaseModel):
    construct_evaluations: List[ConstructEvaluationItem]


class ExpectedEvidenceSchema(BaseModel):
    correct_answer_indicates: str = ""
    distractor_rationale: Dict[str, str] = Field(default_factory=dict)


class GeneratedListeningQuestion(BaseModel):
    id: str
    prompt: str
    options: List[str]
    correct_option_index: int
    target_construct: str
    secondary_constructs: List[str] = Field(default_factory=list)
    question_type: str = "Detail"
    cognitive_objective: str = ""
    difficulty: str = "intermediate"
    expected_evidence: ExpectedEvidenceSchema = Field(default_factory=ExpectedEvidenceSchema)
    weight: float = 1.0
    points: int = 10
    max_replays: int = 2


class GeneratedSpeakingPrompt(BaseModel):
    id: str
    title: str
    instructions: str
    max_time_seconds: int
    target_constructs: List[str]
    followup_eligible: bool


class GeneratedFollowUpDefinition(BaseModel):
    id: str
    parent_prompt_id: str
    prompt_text: str
    target_construct: str
    priority: int = 1
    trigger_conditions: Dict[str, Any] = Field(default_factory=dict)
    expected_evidence_pattern: str = ""
    max_time_seconds: int = 90


class ScenarioGenerationResponse(BaseModel):
    title: str
    description: str
    listening_narration: str
    listening_questions: List[GeneratedListeningQuestion]
    speaking_prompts: List[GeneratedSpeakingPrompt]
    follow_up_definitions: Optional[List[GeneratedFollowUpDefinition]] = None
    construct_mappings: List[str] = Field(default_factory=list)
    expected_behaviour_signals: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
