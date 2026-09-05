from dataclasses import dataclass


@dataclass
class Permission:
    """Domain Entity representing a fine-grained access permission."""

    permission_id: str
    name: str
    description: str

    def __post_init__(self):
        if not self.permission_id or not self.permission_id.strip():
            raise ValueError("Permission permission_id cannot be empty.")
        if not self.name or not self.name.strip():
            raise ValueError("Permission name cannot be empty.")
