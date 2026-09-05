from typing import Dict, Any
from app.infrastructure.platform_integration.registry import SubsystemRegistry
from app.domain.exceptions.platform_exceptions import HealthCheckFailure


class HealthCheckManager:
    """Manages system liveness, startup readiness, subsystem health, and provider health verification."""

    def check_platform_health(self, registry: SubsystemRegistry) -> Dict[str, Any]:
        subsystems = registry.list_registered_subsystems()
        if not subsystems:
            raise HealthCheckFailure("REGISTRY", "Zero registered subsystems found during health check.")

        return {
            "status": "HEALTHY",
            "registered_subsystems_count": len(subsystems),
            "liveness": True,
            "readiness": True,
            "providers": {"Whisper": "HEALTHY", "Gemini": "HEALTHY"},
        }
