"""
==========================================================
Application Enums
==========================================================
"""

from enum import Enum


class AssessmentStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"
    FAILED = "FAILED"


class ModuleType(str, Enum):
    PATTERN = "PatternBot"
    COMPARE = "CompareBot"
    VISION = "VisionBot"
    SOLVER = "SolverBot"


class EventType(str, Enum):
    SESSION_STARTED = "SESSION_STARTED"

    QUESTION_PRESENTED = "QUESTION_PRESENTED"

    ANSWER_SUBMITTED = "ANSWER_SUBMITTED"

    ANSWER_CORRECT = "ANSWER_CORRECT"

    ANSWER_INCORRECT = "ANSWER_INCORRECT"

    HINT_USED = "HINT_USED"

    TIMEOUT = "TIMEOUT"

    MODULE_CHANGED = "MODULE_CHANGED"

    SESSION_FINISHED = "SESSION_FINISHED"


class DifficultyLevel(int, Enum):
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5