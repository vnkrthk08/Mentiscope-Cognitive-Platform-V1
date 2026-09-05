from typing import Set
from app.domain.exceptions.execution_exceptions import ProgressCorruption


class ProgressTracker:
    """Tracks item indices, answered items, remaining items, and completion percentages."""

    def __init__(self, total_items: int = 1):
        if total_items < 1:
            raise ProgressCorruption(0, total_items)
        self.total_items = total_items
        self.current_index: int = 0
        self.answered_item_ids: Set[str] = set()

    def advance_to_next(self) -> int:
        if self.current_index + 1 < self.total_items:
            self.current_index += 1
        return self.current_index

    def mark_answered(self, item_id: str):
        self.answered_item_ids.add(item_id)

    def get_remaining_items_count(self) -> int:
        return max(0, self.total_items - len(self.answered_item_ids))

    def get_completion_percentage(self) -> float:
        return round((len(self.answered_item_ids) / float(self.total_items)) * 100.0, 1)
