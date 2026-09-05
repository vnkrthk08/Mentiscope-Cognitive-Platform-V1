import json
import os
from typing import Any, Dict, Optional
import yaml
from app.core.config import settings
from app.core.logging import logger


class ConfigurationLoader:
    """Centralized configuration manager supporting hot-reloading YAML, JSON, scenario definitions, rubrics, and feature flags."""

    def __init__(self, config_dir: str = settings.CONFIG_REPO_PATH):
        self.config_dir = config_dir
        self._cache: Dict[str, Any] = {}

    def load_yaml(self, relative_path: str) -> Dict[str, Any]:
        file_path = os.path.join(self.config_dir, relative_path)
        if not os.path.exists(file_path):
            logger.warning(f"Configuration file not found at '{file_path}'. Returning empty config.")
            return {}
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            self._cache[relative_path] = data
            return data

    def load_json(self, relative_path: str) -> Dict[str, Any]:
        file_path = os.path.join(self.config_dir, relative_path)
        if not os.path.exists(file_path):
            logger.warning(f"JSON config file not found at '{file_path}'. Returning empty config.")
            return {}
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self._cache[relative_path] = data
            return data

    def get_feature_flag(self, flag_name: str, default: bool = False) -> bool:
        return getattr(settings, flag_name, default)


# Singleton instance
config_loader = ConfigurationLoader()
