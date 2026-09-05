import json
import os
from typing import Any, Dict
import yaml
from app.domain.exceptions.scenario_exceptions import ScenarioLoadFailure


class ScenarioLoader:
    """Parses raw YAML and JSON scenario definition files into raw dictionaries."""

    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise ScenarioLoadFailure(file_path, "File does not exist.")

        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if ext in [".yaml", ".yml"]:
                    data = yaml.safe_load(f)
                elif ext == ".json":
                    data = json.load(f)
                else:
                    raise ScenarioLoadFailure(file_path, f"Unsupported file extension '{ext}'. Must be .yaml, .yml, or .json.")

            if not isinstance(data, dict):
                raise ScenarioLoadFailure(file_path, "Scenario definition root must be a dictionary.")

            return data
        except Exception as e:
            if isinstance(e, ScenarioLoadFailure):
                raise e
            raise ScenarioLoadFailure(file_path, str(e))
