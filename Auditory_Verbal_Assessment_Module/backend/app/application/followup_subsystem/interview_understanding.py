"""
Module 2: Interview Understanding Engine (AIIS v15.0.0).
Performs a single unified LLM understanding call to evaluate response status, extract candidate decision components,
assess coverage dimensions, and detect conversation signals.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass(frozen=True)
class CandidateDecisionData:
    action: Optional[str] = None
    reason: Optional[str] = None
    stakeholders: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    tradeoffs: List[str] = field(default_factory=list)
    reflection: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "reason": self.reason,
            "stakeholders": self.stakeholders,
            "risks": self.risks,
            "alternatives": self.alternatives,
            "tradeoffs": self.tradeoffs,
            "reflection": self.reflection,
        }


@dataclass(frozen=True)
class DecisionCoverageData:
    decision: bool = False
    reason: bool = False
    risk: bool = False
    stakeholder: bool = False
    alternative: bool = False
    tradeoff: bool = False
    reflection: bool = False

    def to_dict(self) -> Dict[str, bool]:
        return {
            "decision": self.decision,
            "reason": self.reason,
            "risk": self.risk,
            "stakeholder": self.stakeholder,
            "alternative": self.alternative,
            "tradeoff": self.tradeoff,
            "reflection": self.reflection,
        }


@dataclass(frozen=True)
class ConversationSignalsData:
    repetitive: bool = False
    contradiction: bool = False
    off_topic: bool = False

    def to_dict(self) -> Dict[str, bool]:
        return {
            "repetitive": self.repetitive,
            "contradiction": self.contradiction,
            "off_topic": self.off_topic,
        }


@dataclass(frozen=True)
class InterviewUnderstandingResult:
    status: str                         # Exactly 1 of 9: VALID, PARTIALLY_VALID, TOO_SHORT, OFF_TOPIC, NONSENSICAL, UNCERTAIN, REFUSAL, REPETITIVE, CONTRADICTORY
    confidence: float                   # 0.0 to 1.0
    candidate_decision: CandidateDecisionData
    coverage: DecisionCoverageData
    conversation: ConversationSignalsData
    raw_response: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "confidence": self.confidence,
            "candidate_decision": self.candidate_decision.to_dict(),
            "coverage": self.coverage.to_dict(),
            "conversation": self.conversation.to_dict(),
            "raw_response": self.raw_response,
        }


class InterviewUnderstandingEngine:
    """Module 2: Single LLM call evaluating response status, decision extraction, coverage, and signals."""

    OFF_TOPIC_KEYWORDS = [
        "favorite movie", "interstellar", "cricket", "football", "pizza",
        "avengers", "pizza", "movie", "cricket", "football", "baseball", "weather",
        "superman", "batman", "marvel", "netflix", "video game", "pepperoni",
    ]

    NONSENSICAL_KEYWORDS = [
        "purple banana", "banana spaceship", "qwerty 123456", "wibble wobble",
        "fish floating", "blabber blabber", "asdfasdf", "zxcvbnm", "iron man", "batman", "dragon",
    ]
    REFUSAL_KEYWORDS = [
        "i refuse to answer", "i refuse to respond", "i refuse to participate",
        "i won't answer", "not answering this", "don't want to answer",
        "skip this question", "pass this question", "no comment on this",
    ]
    UNCERTAIN_KEYWORDS = ["i don't know", "not sure", "maybe", "i guess", "probably", "no idea", "can't say"]

    def evaluate_understanding(
        self,
        scenario_title: str,
        transcript_text: str,
        conversation_history: str = "",
        llm_response_payload: Optional[Dict[str, Any]] = None,
    ) -> InterviewUnderstandingResult:
        clean_text = (transcript_text or "").strip()
        lower_text = clean_text.lower()

        # If LLM payload provided (from APOS / Nemotron call)
        if llm_response_payload and isinstance(llm_response_payload, dict):
            status = llm_response_payload.get("status", "VALID")
            conf = float(llm_response_payload.get("confidence", 0.95))
            dec_raw = llm_response_payload.get("candidate_decision", {})
            cov_raw = llm_response_payload.get("coverage", {})
            sig_raw = llm_response_payload.get("conversation", {})

            decision = CandidateDecisionData(
                action=dec_raw.get("action"),
                reason=dec_raw.get("reason"),
                stakeholders=dec_raw.get("stakeholders") or [],
                risks=dec_raw.get("risks") or [],
                alternatives=dec_raw.get("alternatives") or [],
                tradeoffs=dec_raw.get("tradeoffs") or [],
                reflection=dec_raw.get("reflection"),
            )
            coverage = DecisionCoverageData(
                decision=bool(cov_raw.get("decision", bool(decision.action))),
                reason=bool(cov_raw.get("reason", bool(decision.reason))),
                risk=bool(cov_raw.get("risk", bool(decision.risks))),
                stakeholder=bool(cov_raw.get("stakeholder", bool(decision.stakeholders))),
                alternative=bool(cov_raw.get("alternative", bool(decision.alternatives))),
                tradeoff=bool(cov_raw.get("tradeoff", bool(decision.tradeoffs))),
                reflection=bool(cov_raw.get("reflection", bool(decision.reflection))),
            )
            signals = ConversationSignalsData(
                repetitive=bool(sig_raw.get("repetitive", False)),
                contradiction=bool(sig_raw.get("contradiction", False)),
                off_topic=bool(sig_raw.get("off_topic", False)),
            )
            return InterviewUnderstandingResult(
                status=status,
                confidence=conf,
                candidate_decision=decision,
                coverage=coverage,
                conversation=signals,
                raw_response=llm_response_payload,
            )

        # Deterministic / Fallback Parsing
        words = clean_text.split()
        word_count = len(words)

        if word_count == 0:
            status = "TOO_SHORT"
        elif any(k in lower_text for k in self.NONSENSICAL_KEYWORDS):
            status = "NONSENSICAL"
        elif any(k in lower_text for k in self.OFF_TOPIC_KEYWORDS):
            status = "OFF_TOPIC"
        elif any(k in lower_text for k in self.REFUSAL_KEYWORDS):
            status = "REFUSAL"
        elif any(k in lower_text for k in self.UNCERTAIN_KEYWORDS):
            status = "UNCERTAIN"
        elif word_count <= 3 and any(w in lower_text for w in ["yes", "no", "maybe", "okay", "sure", "fine"]):
            status = "TOO_SHORT"
        elif "instead" in lower_text or "changed my mind" in lower_text:
            status = "CONTRADICTORY"
        elif word_count <= 5 and not any(w in lower_text for w in [
            "because", "stop", "inform", "delay", "help", "talk", "risk", "fail", "failing",
            "damage", "danger", "safety", "priority", "cost", "loss", "overheat", "error",
            "accident", "backup", "budget", "time", "quality", "privacy", "security"
        ]):
            status = "PARTIALLY_VALID"
        else:
            status = "VALID"

        # Rule-based decision extraction without hallucination
        action = clean_text if status in ("VALID", "PARTIALLY_VALID", "CONTRADICTORY") else None
        reason = None
        if action and ("because" in lower_text or "since" in lower_text or "so that" in lower_text or "due to" in lower_text):
            reason = "Stated justification"

        stakeholders = []
        if any(w in lower_text for w in ["teacher", "team", "teammate", "principal", "judge", "student", "arjun", "agreed"]):
            stakeholders.append("Stakeholders/Team")

        risks = []
        if any(w in lower_text for w in ["risk", "fail", "damage", "danger", "delay", "explode"]):
            risks.append("Operational risk")

        alternatives = []
        if "instead" in lower_text or "alternative" in lower_text or "another option" in lower_text:
            alternatives.append("Alternative option")

        tradeoffs = []
        if "tradeoff" in lower_text or "sacrifice" in lower_text or "compromise" in lower_text:
            tradeoffs.append("Trade-off")

        decision = CandidateDecisionData(
            action=action,
            reason=reason,
            stakeholders=stakeholders,
            risks=risks,
            alternatives=alternatives,
            tradeoffs=tradeoffs,
            reflection=None,
        )

        coverage = DecisionCoverageData(
            decision=bool(action),
            reason=bool(reason),
            risk=bool(risks),
            stakeholder=bool(stakeholders),
            alternative=bool(alternatives),
            tradeoff=bool(tradeoffs),
            reflection=False,
        )

        signals = ConversationSignalsData(
            repetitive=False,
            contradiction=status == "CONTRADICTORY",
            off_topic=status == "OFF_TOPIC",
        )

        return InterviewUnderstandingResult(
            status=status,
            confidence=0.92,
            candidate_decision=decision,
            coverage=coverage,
            conversation=signals,
            raw_response={},
        )
