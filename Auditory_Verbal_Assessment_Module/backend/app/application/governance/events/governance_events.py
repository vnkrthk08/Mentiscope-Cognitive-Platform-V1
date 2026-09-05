"""Governance Domain Events."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid


@dataclass
class GovernanceEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelRegisteredEvent(GovernanceEvent):
    def __post_init__(self):
        self.event_type = "MODEL_REGISTERED"


@dataclass
class ConfigurationSnapshotCreatedEvent(GovernanceEvent):
    def __post_init__(self):
        self.event_type = "CONFIGURATION_SNAPSHOT_CREATED"


@dataclass
class ExperimentCreatedEvent(GovernanceEvent):
    def __post_init__(self):
        self.event_type = "EXPERIMENT_CREATED"


@dataclass
class ExperimentCompletedEvent(GovernanceEvent):
    def __post_init__(self):
        self.event_type = "EXPERIMENT_COMPLETED"


@dataclass
class ComparisonReportGeneratedEvent(GovernanceEvent):
    def __post_init__(self):
        self.event_type = "COMPARISON_REPORT_GENERATED"
