"""
Module 1: Behavioral Evidence Extraction Engine.
Extracts verbatim quotes, behavioral indicators, and cognitive signals across 11 constructs.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class EvidenceItem:
    construct: str
    verbatim_quote: str
    indicator: str
    confidence: float


class BehavioralEvidenceExtractor:
    """Extracts observable behavioral evidence across 11 constructs from transcripts."""

    CONSTRUCT_KEYWORDS = {
        "COMMUNICATION": ["explain", "communicate", "clarify", "discuss", "inform", "speak", "present"],
        "REASONING": ["because", "therefore", "reason", "logic", "since", "consequently", "due to"],
        "DECISION_MAKING": ["choose", "decide", "select", "opt", "priority", "trade-off", "plan"],
        "LEADERSHIP": ["lead", "delegate", "guide", "organize", "team", "coordinate", "direct"],
        "CONFIDENCE": ["certainly", "definitely", "sure", "confident", "will achieve", "no doubt"],
        "ADAPTABILITY": ["pivot", "adjust", "change", "switch", "alternative", "flexibility", "modify"],
        "RISK_AWARENESS": ["risk", "safety", "danger", "precaution", "hazard", "threat", "mitigate"],
        "ETHICAL_AWARENESS": ["fair", "honest", "integrity", "ethics", "rules", "transparent", "moral"],
        "EMOTIONAL_REGULATION": ["calm", "patient", "composure", "steady", "pause", "listen"],
        "PROBLEM_SOLVING": ["fix", "resolve", "solution", "repair", "debug", "overcome", "solve"],
        "CRITICAL_THINKING": ["analyze", "evaluate", "compare", "assess", "examine", "investigate"],
    }

    def extract_evidence(self, transcript_text: str, target_constructs: List[str] = None) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []
        if not transcript_text or len(transcript_text.strip()) < 5:
            return items

        sentences = [s.strip() for s in re.split(r"[.!?]", transcript_text) if len(s.strip()) > 3]

        for sentence in sentences:
            sentence_lower = sentence.lower()

            for construct, keywords in self.CONSTRUCT_KEYWORDS.items():
                if target_constructs and construct not in target_constructs and construct.lower() not in [c.lower() for c in target_constructs]:
                    continue

                matched_kw = [kw for kw in keywords if kw in sentence_lower]
                if matched_kw:
                    conf = min(0.4 + (len(matched_kw) * 0.25), 0.95)
                    items.append(
                        EvidenceItem(
                            construct=construct,
                            verbatim_quote=sentence,
                            indicator=f"Demonstrates {construct.lower().replace('_', ' ')} using key signal '{matched_kw[0]}'",
                            confidence=round(conf, 2),
                        )
                    )

        # Fallback if no specific keywords matched
        if not items and sentences:
            primary_c = target_constructs[0] if target_constructs else "COMMUNICATION"
            items.append(
                EvidenceItem(
                    construct=primary_c,
                    verbatim_quote=sentences[0],
                    indicator=f"General response provided for {primary_c}",
                    confidence=0.45,
                )
            )

        return items
