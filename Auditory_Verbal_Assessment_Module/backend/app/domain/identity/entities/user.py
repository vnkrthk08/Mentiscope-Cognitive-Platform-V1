import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
from app.domain.identity.entities.role import Role

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


@dataclass
class User:
    """Domain Entity representing a user of the MentiScope platform."""

    user_id: str
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    roles: List[Role] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User user_id cannot be empty.")
        if not self.username or len(self.username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters.")
        if not self.email or not EMAIL_REGEX.match(self.email):
            raise ValueError("Invalid email format.")
        if not self.hashed_password:
            raise ValueError("Hashed password cannot be empty.")

    @property
    def permissions(self) -> List[str]:
        """Flattened list of all permission names assigned to user's roles."""
        perms = set()
        for role in self.roles:
            for p in role.permissions:
                perms.add(p.name)
        return sorted(list(perms))

    def has_permission(self, permission_name: str) -> bool:
        """Helper checking if user has specific permission name."""
        return permission_name in self.permissions
