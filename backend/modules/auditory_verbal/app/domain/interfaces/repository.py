from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class IRepository(ABC, Generic[T, ID]):
    """Abstract Base Class for generic domain repositories (Clean Architecture interface)."""

    @abstractmethod
    async def get_by_id(self, entity_id: ID) -> Optional[T]:
        pass

    @abstractmethod
    async def list_all(self) -> List[T]:
        pass

    @abstractmethod
    async def save(self, entity: T) -> T:
        pass

    @abstractmethod
    async def delete(self, entity_id: ID) -> bool:
        pass
