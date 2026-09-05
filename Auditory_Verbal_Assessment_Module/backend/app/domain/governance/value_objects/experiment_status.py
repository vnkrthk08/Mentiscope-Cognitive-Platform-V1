"""ExperimentStatus Value Object."""
from enum import Enum


class ExperimentStatus(str, Enum):
    DRAFT = "DRAFT"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"
