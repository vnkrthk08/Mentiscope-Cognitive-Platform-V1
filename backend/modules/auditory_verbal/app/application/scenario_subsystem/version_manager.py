from typing import Dict
from app.domain.value_objects.scenario_version import ScenarioVersion
from app.domain.exceptions.scenario_exceptions import VersionMismatch, InvalidScenarioVersion


class ScenarioVersionManager:
    """Manages SemVer compatibility, deprecation flags, and version comparison for scenario packs."""

    def __init__(self):
        self._deprecated_versions: Dict[str, str] = {}  # scenario_id -> version_str

    def mark_deprecated(self, scenario_id: str, version_str: str):
        self._deprecated_versions[scenario_id] = version_str

    def is_deprecated(self, scenario_id: str, version_str: str) -> bool:
        return self._deprecated_versions.get(scenario_id) == version_str

    def compare_versions(self, ver1: str, ver2: str) -> int:
        """Returns 1 if ver1 > ver2, -1 if ver1 < ver2, 0 if equal."""
        try:
            v1_parts = [int(p) for p in ver1.split(".")]
            v2_parts = [int(p) for p in ver2.split(".")]
        except Exception:
            raise InvalidScenarioVersion(f"{ver1} or {ver2}", "Parsing failed")

        if v1_parts > v2_parts:
            return 1
        elif v1_parts < v2_parts:
            return -1
        return 0

    def assert_compatible(self, required_ver: str, actual_ver: str):
        v1_major = required_ver.split(".")[0]
        v2_major = actual_ver.split(".")[0]
        if v1_major != v2_major:
            raise VersionMismatch(required_ver, actual_ver)
