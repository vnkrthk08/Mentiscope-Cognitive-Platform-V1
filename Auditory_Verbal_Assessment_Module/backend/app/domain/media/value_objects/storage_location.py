from dataclasses import dataclass


@dataclass(frozen=True)
class StorageLocation:
    """Immutable Value Object tracking file storage locations."""

    provider_name: str
    bucket_name: str
    object_key: str
    download_endpoint: str

    def __post_init__(self):
        if not self.provider_name or not self.provider_name.strip():
            raise ValueError("StorageLocation provider_name cannot be empty.")
        if not self.bucket_name or not self.bucket_name.strip():
            raise ValueError("StorageLocation bucket_name cannot be empty.")
        if not self.object_key or not self.object_key.strip():
            raise ValueError("StorageLocation object_key cannot be empty.")
