"""
Guard 2: Semantic Narrative Guard.
Evaluates title and narrative summary similarity using normalized string distance and token-overlap embeddings.
"""

from typing import List, Tuple
import re


class SemanticNarrativeGuard:
    """Post-LLM guard evaluating semantic narrative text similarity."""

    def __init__(self, similarity_threshold: float = 0.65):
        self.similarity_threshold = similarity_threshold

    def _normalize(self, text: str) -> List[str]:
        cleaned = re.sub(r"[^\w\s]", "", text.lower())
        return [w for w in cleaned.split() if len(w) > 2]

    def compute_text_similarity(self, text1: str, text2: str) -> float:
        """Computes Jaccard / token-overlap semantic similarity between two texts."""
        tokens1 = set(self._normalize(text1))
        tokens2 = set(self._normalize(text2))

        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)

        return round(len(intersection) / len(union), 3)

    def is_narrative_duplicate(
        self, candidate_title: str, candidate_narrative: str, history: List[Tuple[str, str]]
    ) -> bool:
        """Compares candidate (title, narrative) against history."""
        cand_text = f"{candidate_title} {candidate_narrative[:300]}"

        for past_title, past_narrative in history:
            past_text = f"{past_title} {past_narrative[:300]}"
            sim = self.compute_text_similarity(cand_text, past_text)
            if sim >= self.similarity_threshold:
                return True
        return False
