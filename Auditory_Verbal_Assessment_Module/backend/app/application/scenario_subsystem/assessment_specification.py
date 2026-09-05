"""
Decomposed Assessment Specification Models & Structural Fingerprint.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
import hashlib

from app.application.scenario_subsystem.assessment_skeleton import AssessmentSkeleton
from app.application.scenario_subsystem.scenario_skeleton import ScenarioSkeleton
from app.application.scenario_subsystem.scenario_grammar import ScenarioGrammar
from app.application.scenario_subsystem.interaction_model import InteractionModel


@dataclass(frozen=True)
class NarrativeBeat:
    purpose: str       # SETTING, STAKEHOLDER_SETUP, TRIGGER, ESCALATION, DECISION_POINT
    focus: str         # Content focus
    stakeholder_ref: str # Stakeholder involved

    def to_dict(self) -> Dict[str, str]:
        return {
            "purpose": self.purpose,
            "focus": self.focus,
            "stakeholder_ref": self.stakeholder_ref,
        }


@dataclass(frozen=True)
class NarrativePlan:
    beats: Tuple[NarrativeBeat, ...]

    def to_dict(self) -> List[Dict[str, str]]:
        return [b.to_dict() for b in self.beats]


@dataclass(frozen=True)
class MCQSpecification:
    question_number: int
    target_construct: str
    cognitive_depth: str
    prompt_intent: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_number": self.question_number,
            "target_construct": self.target_construct,
            "cognitive_depth": self.cognitive_depth,
            "prompt_intent": self.prompt_intent,
        }


@dataclass(frozen=True)
class ListeningPlan:
    mcqs: Tuple[MCQSpecification, ...]

    def to_dict(self) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in self.mcqs]


@dataclass(frozen=True)
class SpeakingSpecification:
    stage_number: int
    stage_name: str
    target_constructs: Tuple[str, ...]
    prompt_intent: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_number": self.stage_number,
            "stage_name": self.stage_name,
            "target_constructs": list(self.target_constructs),
            "prompt_intent": self.prompt_intent,
        }


@dataclass(frozen=True)
class SpeakingPlan:
    prompts: Tuple[SpeakingSpecification, ...]

    def to_dict(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self.prompts]


@dataclass(frozen=True)
class StructuralFingerprint:
    intent: str
    grammar: str
    interaction: str
    decision_type: str
    stakeholder_pattern: str
    resource_pattern: str
    escalation_pattern: str
    narrative_pattern: str
    mcq_pattern: str
    speaking_pattern: str

    def compute_hash(self) -> str:
        raw = (
            f"{self.intent}|{self.grammar}|{self.interaction}|"
            f"{self.decision_type}|{self.stakeholder_pattern}|"
            f"{self.escalation_pattern}"
        )
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, str]:
        return {
            "intent": self.intent,
            "grammar": self.grammar,
            "interaction": self.interaction,
            "decision_type": self.decision_type,
            "stakeholder_pattern": self.stakeholder_pattern,
            "resource_pattern": self.resource_pattern,
            "escalation_pattern": self.escalation_pattern,
            "narrative_pattern": self.narrative_pattern,
            "mcq_pattern": self.mcq_pattern,
            "speaking_pattern": self.speaking_pattern,
            "hash": self.compute_hash(),
        }


@dataclass(frozen=True)
class AssessmentSpecification:
    assessment_skeleton: AssessmentSkeleton
    scenario_skeleton: ScenarioSkeleton
    grammar: ScenarioGrammar
    interaction_model: InteractionModel
    narrative_plan: NarrativePlan
    listening_plan: ListeningPlan
    speaking_plan: SpeakingPlan
    fingerprint: StructuralFingerprint

    def to_dict(self) -> Dict[str, Any]:
        return {
            "assessment_skeleton": self.assessment_skeleton.to_dict(),
            "scenario_skeleton": self.scenario_skeleton.to_dict(),
            "grammar": self.grammar.name,
            "interaction_model": self.interaction_model.name,
            "narrative_plan": self.narrative_plan.to_dict(),
            "listening_plan": self.listening_plan.to_dict(),
            "speaking_plan": self.speaking_plan.to_dict(),
            "fingerprint": self.fingerprint.to_dict(),
        }
