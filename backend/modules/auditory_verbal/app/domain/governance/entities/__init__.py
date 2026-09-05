"""Governance Entities package."""
from app.domain.governance.entities.model_registry import RegisteredModel
from app.domain.governance.entities.configuration_snapshot import ConfigurationSnapshot
from app.domain.governance.entities.experiment import Experiment
from app.domain.governance.entities.experiment_run import ExperimentRun
from app.domain.governance.entities.comparison_report import ComparisonReport

__all__ = [
    "RegisteredModel",
    "ConfigurationSnapshot",
    "Experiment",
    "ExperimentRun",
    "ComparisonReport",
]
