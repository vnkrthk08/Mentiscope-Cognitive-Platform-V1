from typing import Dict, Any, Optional
from app.domain.exceptions.platform_exceptions import ConfigurationFailure


class ConfigurationManager:
    """Manages environment configuration, feature flags, provider settings, and runtime config validation."""

    def __init__(self, env: str = "production"):
        self.env = env
        self._feature_flags: Dict[str, bool] = {
            "ENABLE_ADAPTIVE_FOLLOWUP": True,
            "ENABLE_LLM_EVALUATION": True,
            "ENABLE_RESEARCH_ANALYTICS": True,
            "STRICT_SECURITY_POLICIES": True,
        }
        self._config: Dict[str, Any] = {
            "ENVIRONMENT": env,
            "SPEECH_PROVIDER": "Whisper",
            "LLM_PROVIDER": "Gemini",
            "DEFAULT_CALIBRATION_MODEL": "1.0.0",
        }

    def validate_configuration(self) -> bool:
        if not self._config.get("ENVIRONMENT"):
            raise ConfigurationFailure("ENVIRONMENT", "Environment config is empty.")
        return True

    def get_feature_flag(self, flag_name: str, default: bool = False) -> bool:
        return self._feature_flags.get(flag_name, default)

    def get_config_summary(self) -> str:
        return f"Env: {self.env} | Active Feature Flags: {len(self._feature_flags)}"
