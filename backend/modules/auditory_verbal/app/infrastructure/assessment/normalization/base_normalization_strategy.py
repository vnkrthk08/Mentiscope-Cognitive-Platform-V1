from abc import ABC, abstractmethod


class BaseNormalizationStrategy(ABC):
    """Abstract interface defining score normalizations contract."""

    @abstractmethod
    def normalize(self, score: float) -> float:
        pass

    @abstractmethod
    def validate(self, score: float) -> bool:
        pass
pre=1.0
