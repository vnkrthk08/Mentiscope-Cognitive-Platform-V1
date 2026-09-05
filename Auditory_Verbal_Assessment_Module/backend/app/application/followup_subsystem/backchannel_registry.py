"""
Module 8.6: Backchannel Registry & Canary Router (AIIS v20.2 Architecture).

Maintains a curated registry of 32 content-agnostic conversational acknowledgments
(backchannel turn bridges) with strict session-level LRU rotation (no repetition within 8 turns).
Also provides deterministic session-level canary routing via CRC32 hashing.
"""

import zlib
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set


@dataclass
class BackchannelSelection:
    text: str
    category: str
    turn_index: int


class BackchannelRegistry:
    """Registry of 32 natural conversational acknowledgments with session-level LRU memory."""

    # 32 Curated, content-agnostic conversational backchannel bridges
    CATEGORIES: Dict[str, List[str]] = {
        "COGNITIVE": [
            "Understood, let's explore your thinking there.",
            "That's clear, let's look closer at that.",
            "I see your reasoning on that.",
            "Got it, that gives good context.",
            "Understood, let's dig into that rationale.",
            "I hear the logic behind that approach.",
            "That's a helpful overview of your thinking.",
            "Clear, let's unpack that perspective.",
        ],
        "ACTION_STANCE": [
            "Thanks for outlining that plan.",
            "Got it, looking at that decision.",
            "Understood on that initial step.",
            "That makes sense for this scenario.",
            "Noted on how you would structure that action.",
            "Thanks for clarifying how you would proceed.",
            "I see the direction you're taking with that.",
            "Understood on that chosen course of action.",
        ],
        "ANALYTICAL": [
            "I see the consideration there.",
            "That's an important angle to look at.",
            "Understood on how you prioritized that factor.",
            "Noted on how you approached that balance.",
            "That's a thoughtful way to frame the challenge.",
            "I understand the factors you were weighing.",
            "Makes sense in terms of how you evaluated that.",
            "That highlights a key dynamic in this situation.",
        ],
        "FORWARD_LOOKING": [
            "Thanks for walking me through that.",
            "I hear your point on that.",
            "Let's look a bit deeper into that approach.",
            "Got it, let's take that a step further.",
            "Appreciate you sharing that perspective.",
            "Understood, let's expand on that thought.",
            "That's clear, let's examine the next layer.",
            "Good, let's consider the broader implications.",
        ],
    }

    def __init__(self, memory_window: int = 8):
        self.memory_window = memory_window
        self._session_history: Dict[str, List[str]] = {}

    def get_all_phrases(self) -> List[str]:
        """Returns flat list of all 32 backchannel phrases."""
        phrases = []
        for cat_list in self.CATEGORIES.values():
            phrases.extend(cat_list)
        return phrases

    def select_backchannel(
        self,
        session_id: str,
        turn_number: int = 1,
        preferred_category: Optional[str] = None,
    ) -> BackchannelSelection:
        """
        Selects a conversational backchannel ensuring no repetition within the session's LRU memory window.
        Rotates across categories to maintain tonal variety.
        """
        used = self._session_history.setdefault(session_id, [])

        # Rotate category based on turn_number if preferred_category not specified
        category_names = list(self.CATEGORIES.keys())
        cat_idx = (turn_number - 1) % len(category_names)
        target_cat = preferred_category if (preferred_category and preferred_category in self.CATEGORIES) else category_names[cat_idx]

        candidates = [p for p in self.CATEGORIES[target_cat] if p not in used]

        # If all candidates in target category were recently used, search all unused across all categories
        if not candidates:
            all_phrases = self.get_all_phrases()
            candidates = [p for p in all_phrases if p not in used]

        # If still empty (session has exceeded full pool without clearing), reset oldest half of history
        if not candidates:
            used = used[-(self.memory_window // 2):]
            self._session_history[session_id] = used
            candidates = [p for p in self.CATEGORIES[target_cat] if p not in used] or self.get_all_phrases()

        selected_text = candidates[0]

        # Update session LRU history
        used.append(selected_text)
        if len(used) > self.memory_window:
            used.pop(0)
        self._session_history[session_id] = used

        return BackchannelSelection(
            text=selected_text,
            category=target_cat,
            turn_index=turn_number,
        )

    def clear_session(self, session_id: str) -> None:
        """Cleans up session history when assessment completes."""
        self._session_history.pop(session_id, None)

    @classmethod
    def is_canary_session(cls, session_id: str, rollout_percentage: int) -> bool:
        """
        Deterministically assigns a session to the canary streaming cohort based on CRC32 hashing.
        Returns True if hash(session_id) % 100 < rollout_percentage.
        Ensures a student session consistently uses streaming (or unary) across all turns.
        """
        if rollout_percentage <= 0:
            return False
        if rollout_percentage >= 100:
            return True
        if not session_id:
            return False

        hash_val = zlib.crc32(session_id.encode("utf-8")) & 0xFFFFFFFF
        return (hash_val % 100) < rollout_percentage


# Global singleton instance for app-wide lifecycle
backchannel_registry = BackchannelRegistry()
