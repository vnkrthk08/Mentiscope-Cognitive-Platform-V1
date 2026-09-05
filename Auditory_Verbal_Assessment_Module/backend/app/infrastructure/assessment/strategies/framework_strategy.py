from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.domain.construct.entities.construct_profile import ConstructProfile
from app.domain.assessment.entities.framework_result import FrameworkResult
from app.domain.assessment.entities.scoring_policy import ScoringPolicy


class FrameworkScoringStrategy(ABC):
    """Abstract interface for all framework-specific scoring strategies."""

    @abstractmethod
    def calculate(self, profiles: List[ConstructProfile], policy: ScoringPolicy) -> FrameworkResult:
        """Calculates raw & normalized scores, confidence and summaries for this framework."""
        pass

    @abstractmethod
    def validate(self, profiles: List[ConstructProfile], policy: ScoringPolicy) -> List[str]:
        """Validates input construct profiles parameters for conflicts or omissions."""
        pass
pre=1.0
