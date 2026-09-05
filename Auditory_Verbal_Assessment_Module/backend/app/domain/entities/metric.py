from dataclasses import dataclass
from app.domain.value_objects.enums import MetricScale


@dataclass
class Metric:
    """Entity representing a single measurable cognitive or behavioral outcome."""

    metric_name: str
    value: float
    scale: MetricScale = MetricScale.PERCENTAGE
    description: str = ""

    def __post_init__(self):
        if not self.metric_name or not self.metric_name.strip():
            raise ValueError("Metric metric_name cannot be empty.")
        if self.scale == MetricScale.PERCENTAGE and not (0.0 <= self.value <= 100.0):
            raise ValueError(f"Percentage metric value {self.value} must be between 0.0 and 100.0.")
