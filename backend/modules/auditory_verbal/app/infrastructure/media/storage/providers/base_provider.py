from abc import ABC, abstractmethod
from typing import Dict, Any


class StorageProvider(ABC):
    """Abstract interface defining the contract for object storage providers."""

    @abstractmethod
    async def generate_upload_url(self, bucket_name: str, object_key: str, expires_in: int = 3600) -> str:
        """Generates a presigned URL that clients can use to perform direct uploads."""
        pass

    @abstractmethod
    async def generate_download_url(self, bucket_name: str, object_key: str, expires_in: int = 3600) -> str:
        """Generates a presigned URL that client-agents can use to perform secure downloads."""
        pass

    @abstractmethod
    async def complete_upload(self, bucket_name: str, object_key: str) -> bool:
        """Finalizes chunked uploads and verifies upload success."""
        pass

    @abstractmethod
    async def delete_asset(self, bucket_name: str, object_key: str) -> bool:
        """Deletes media file permanently from the bucket/container."""
        pass

    @abstractmethod
    async def asset_exists(self, bucket_name: str, object_key: str) -> bool:
        """Verifies if an object is present in storage."""
        pass

    @abstractmethod
    async def get_metadata(self, bucket_name: str, object_key: str) -> Dict[str, Any]:
        """Loads provider specific headers and configuration metadata from file."""
        pass
