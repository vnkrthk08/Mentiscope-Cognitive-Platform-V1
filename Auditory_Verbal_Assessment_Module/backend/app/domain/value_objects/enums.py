from enum import Enum


class AssessmentStage(str, Enum):
    DEVICE_CHECK = "DEVICE_CHECK"
    INSTRUCTIONS = "INSTRUCTIONS"
    PRACTICE = "PRACTICE"
    SCENARIO_PRESENTATION = "SCENARIO_PRESENTATION"
    LISTENING_ASSESSMENT = "LISTENING_ASSESSMENT"
    SPEAKING_ASSESSMENT = "SPEAKING_ASSESSMENT"
    ADAPTIVE_FOLLOWUP = "ADAPTIVE_FOLLOWUP"
    EVIDENCE_EXTRACTION = "EVIDENCE_EXTRACTION"
    CONSTRUCT_EVALUATION = "CONSTRUCT_EVALUATION"
    DETERMINISTIC_SCORING = "DETERMINISTIC_SCORING"
    REPORT_GENERATION = "REPORT_GENERATION"
    COMPLETED = "COMPLETED"


class SessionStatus(str, Enum):
    INITIALIZED = "INITIALIZED"
    IN_PROGRESS = "IN_PROGRESS"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    TIMED_OUT = "TIMED_OUT"
    FAILED = "FAILED"


class ConstructType(str, Enum):
    LISTENING_ABILITY = "LISTENING_ABILITY"
    LISTENING_COMPREHENSION = "LISTENING_COMPREHENSION"
    ATTENTION = "ATTENTION"
    WORKING_MEMORY = "WORKING_MEMORY"
    COMMUNICATION = "COMMUNICATION"
    REASONING = "REASONING"
    DECISION_MAKING = "DECISION_MAKING"
    ETHICAL_REASONING = "ETHICAL_REASONING"
    ADAPTABILITY = "ADAPTABILITY"
    RESPONSIBILITY = "RESPONSIBILITY"
    CONFIDENCE = "CONFIDENCE"

    @classmethod
    def from_str(cls, val: str) -> "ConstructType":
        if isinstance(val, cls):
            return val
        norm = str(val).strip().upper().replace(" ", "_").replace("-", "_")
        if norm == "LISTEN_COMPREHENSION":
            norm = "LISTENING_COMPREHENSION"
        try:
            return cls[norm]
        except KeyError:
            try:
                return cls(norm)
            except ValueError:
                for member in cls:
                    if member.value == norm or member.name == norm:
                        return member
                return cls.LISTENING_ABILITY


class DifficultyLevel(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


class EvidenceType(str, Enum):
    VERBATIM_QUOTE = "VERBATIM_QUOTE"
    BEHAVIORAL_INDICATOR = "BEHAVIORAL_INDICATOR"
    ACOUSTIC_TEMPO = "ACOUSTIC_TEMPO"
    PAUSE_PATTERN = "PAUSE_PATTERN"
    RULE_MATCH = "RULE_MATCH"


class PolarityType(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


class PromptType(str, Enum):
    SCENARIO_NARRATIVE = "SCENARIO_NARRATIVE"
    SPEAKING_TASK = "SPEAKING_TASK"
    ADAPTIVE_PROBE = "ADAPTIVE_PROBE"
    EVIDENCE_EXTRACTION_SYSTEM = "EVIDENCE_EXTRACTION_SYSTEM"
    REPAIR_PROMPT = "REPAIR_PROMPT"


class Language(str, Enum):
    EN_US = "en-US"
    EN_GB = "en-GB"
    EN_IN = "en-IN"


class ProviderType(str, Enum):
    OPENAI = "OPENAI"
    GEMINI = "GEMINI"
    CLAUDE = "CLAUDE"
    WHISPER = "WHISPER"
    DEEPGRAM = "DEEPGRAM"


class MetricScale(str, Enum):
    PERCENTAGE = "PERCENTAGE"  # 0 to 100
    STANINE = "STANINE"        # 1 to 9
    Z_SCORE = "Z_SCORE"        # Standardized
