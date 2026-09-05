from typing import Dict, List
from app.domain.exceptions.execution_exceptions import ReplayLimitExceeded


class ReplayManager:
    """Tracks audio replay counts and enforces item-level replay policies."""

    def __init__(self):
        self._replay_counts: Dict[str, int] = {}
        self._history: Dict[str, List[float]] = {}

    def get_replay_count(self, item_id: str) -> int:
        return self._replay_counts.get(item_id, 0)

    def record_replay(self, item_id: str, max_replays: int) -> int:
        current = self.get_replay_count(item_id)
        if current >= max_replays:
            raise ReplayLimitExceeded(item_id, max_replays)

        self._replay_counts[item_id] = current + 1
        return self._replay_counts[item_id]

    def get_remaining_replays(self, item_id: str, max_replays: int) -> int:
        current = self.get_replay_count(item_id)
        return max(0, max_replays - current)
