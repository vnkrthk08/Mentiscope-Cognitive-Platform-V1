from dataclasses import dataclass, field
from typing import List
from app.domain.identity.entities.permission import Permission


@dataclass
class Role:
    """Domain Entity representing a collection of privileges."""

    role_id: str
    name: str
    permissions: List[Permission] = field(default_factory=list)

    def __post_init__(self):
        if not self.role_id or not self.role_id.strip():
            raise ValueError("Role role_id cannot be empty.")
        if not self.name or not self.name.strip():
            raise ValueError("Role name cannot be empty.")
