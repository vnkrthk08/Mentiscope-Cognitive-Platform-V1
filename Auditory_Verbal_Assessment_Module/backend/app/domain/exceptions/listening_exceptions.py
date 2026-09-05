class ListeningEngineException(Exception):
    """Base exception for Listening Assessment Engine errors."""

    pass


class ListeningModuleMissing(ListeningEngineException):
    def __init__(self, scenario_id: str):
        super().__init__(f"Scenario '{scenario_id}' is missing a valid listening module configuration.")


class AudioPlaybackFailure(ListeningEngineException):
    def __init__(self, url: str, reason: str):
        super().__init__(f"Audio playback error for URL '{url}': {reason}")


class AudioNotLoaded(ListeningEngineException):
    def __init__(self, scenario_id: str):
        super().__init__(f"Audio asset for scenario '{scenario_id}' has not been loaded.")


class InvalidAnswerOption(ListeningEngineException):
    def __init__(self, question_id: str, selected_index: int, total_options: int):
        super().__init__(f"Invalid option index {selected_index} selected for question '{question_id}' (total options: {total_options}).")


class QuestionNotFound(ListeningEngineException):
    def __init__(self, question_id: str, scenario_id: str):
        super().__init__(f"Listening question '{question_id}' not found in scenario '{scenario_id}'.")


class ReplayDenied(ListeningEngineException):
    def __init__(self, item_id: str, max_replays: int):
        super().__init__(f"Replay request denied for item '{item_id}'. Exceeds max limit of {max_replays}.")


class ListeningValidationError(ListeningEngineException):
    def __init__(self, reason: str):
        super().__init__(f"Listening assessment validation error: {reason}")


class ListeningSessionFailure(ListeningEngineException):
    def __init__(self, session_id: str, reason: str):
        super().__init__(f"Listening assessment session '{session_id}' failed: {reason}")
