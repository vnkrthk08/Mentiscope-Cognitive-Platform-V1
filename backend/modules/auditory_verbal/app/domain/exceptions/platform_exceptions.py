class PlatformIntegrationException(Exception):
    """Base exception for Platform Integration, Security, Operations & Production Readiness errors."""

    pass


class PlatformStartupFailure(PlatformIntegrationException):
    def __init__(self, reason: str):
        super().__init__(f"Platform startup sequence failed: {reason}")


class SubsystemRegistrationFailure(PlatformIntegrationException):
    def __init__(self, subsystem_name: str, reason: str):
        super().__init__(f"Subsystem registration failed for '{subsystem_name}': {reason}")


class ConfigurationFailure(PlatformIntegrationException):
    def __init__(self, config_key: str, reason: str):
        super().__init__(f"Platform configuration validation error for '{config_key}': {reason}")


class SecurityInitializationFailure(PlatformIntegrationException):
    def __init__(self, policy_name: str, reason: str):
        super().__init__(f"Security policy initialization failed for '{policy_name}': {reason}")


class HealthCheckFailure(PlatformIntegrationException):
    def __init__(self, target: str, reason: str):
        super().__init__(f"Platform health check failed for '{target}': {reason}")


class DeploymentFailure(PlatformIntegrationException):
    def __init__(self, manifest_id: str, reason: str):
        super().__init__(f"Deployment manifest validation error for '{manifest_id}': {reason}")
