class ScenarioException(Exception):
    """Base domain exception for Scenario Management System."""

    pass


class ScenarioNotFound(ScenarioException):
    def __init__(self, scenario_id: str):
        self.scenario_id = scenario_id
        super().__init__(f"Scenario with ID '{scenario_id}' was not found in the repository.")


class ScenarioValidationError(ScenarioException):
    def __init__(self, scenario_id: str, errors: list):
        self.scenario_id = scenario_id
        self.errors = errors
        super().__init__(f"Validation failed for scenario '{scenario_id}': {', '.join(errors)}")


class DuplicateScenarioID(ScenarioException):
    def __init__(self, scenario_id: str):
        self.scenario_id = scenario_id
        super().__init__(f"Duplicate scenario ID detected: '{scenario_id}'.")


class InvalidScenarioVersion(ScenarioException):
    def __init__(self, version_str: str, reason: str = ""):
        self.version_str = version_str
        super().__init__(f"Invalid scenario version '{version_str}': {reason}")


class MissingConstructMapping(ScenarioException):
    def __init__(self, scenario_id: str, item_id: str, item_type: str):
        self.item_id = item_id
        self.item_type = item_type
        super().__init__(f"Missing construct mapping for {item_type} item '{item_id}' in scenario '{scenario_id}'.")


class MissingAudioAsset(ScenarioException):
    def __init__(self, asset_url: str):
        self.asset_url = asset_url
        super().__init__(f"Required audio asset not found or invalid at URL: '{asset_url}'.")


class InvalidReplayPolicy(ScenarioException):
    def __init__(self, item_id: str, replays: int):
        super().__init__(f"Invalid replay policy for item '{item_id}': max_replays cannot be negative ({replays}).")


class ScenarioLoadFailure(ScenarioException):
    def __init__(self, file_path: str, reason: str):
        super().__init__(f"Failed to load scenario file from '{file_path}': {reason}")


class VersionMismatch(ScenarioException):
    def __init__(self, required_ver: str, actual_ver: str):
        super().__init__(f"Scenario version mismatch: Required '{required_ver}', but found '{actual_ver}'.")
