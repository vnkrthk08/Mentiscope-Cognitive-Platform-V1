class ResearchFrameworkException(Exception):
    """Base exception for Research, Analytics, Validation & Monitoring Framework errors."""

    pass


class AnalyticsFailure(ResearchFrameworkException):
    def __init__(self, reason: str):
        super().__init__(f"Research analytics processing failed: {reason}")


class ValidationFailure(ResearchFrameworkException):
    def __init__(self, reason: str):
        super().__init__(f"Psychometric validation check failed: {reason}")


class MonitoringFailure(ResearchFrameworkException):
    def __init__(self, subsystem_name: str, reason: str):
        super().__init__(f"Platform monitoring alert for '{subsystem_name}': {reason}")


class ExperimentFailure(ResearchFrameworkException):
    def __init__(self, experiment_id: str, reason: str):
        super().__init__(f"Experiment '{experiment_id}' execution failed: {reason}")


class MetricCollectionFailure(ResearchFrameworkException):
    def __init__(self, metric_name: str, reason: str):
        super().__init__(f"Failed to collect research metric '{metric_name}': {reason}")


class DashboardGenerationFailure(ResearchFrameworkException):
    def __init__(self, reason: str):
        super().__init__(f"Research dashboard model generation failed: {reason}")
