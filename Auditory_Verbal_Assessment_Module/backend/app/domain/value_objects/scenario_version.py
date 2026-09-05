from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ScenarioVersion:
    """Immutable Value Object enforcing semantic versioning (MAJOR.MINOR.PATCH)."""

    version_str: str

    def __post_init__(self):
        semver_regex = r"^\d+\.\d+\.\d+$"
        if not re.match(semver_regex, self.version_str):
            raise ValueError(f"Invalid scenario version format '{self.version_str}'. Must follow SemVer 'X.Y.Z'.")

    def __str__(self) -> str:
        return self.version_str
