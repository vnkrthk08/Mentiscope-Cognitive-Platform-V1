from dataclasses import dataclass


@dataclass(frozen=True)
class BehaviorIndicator:
    """Immutable Value Object storing indicator taxonomy classification."""

    indicator_name: str
    indicator_category: str

    def __post_init__(self):
        if not self.indicator_name or not self.indicator_name.strip():
            raise ValueError("BehaviorIndicator indicator_name cannot be empty.")
        if not self.indicator_category or not self.indicator_category.strip():
            raise ValueError("BehaviorIndicator indicator_category cannot be empty.")
