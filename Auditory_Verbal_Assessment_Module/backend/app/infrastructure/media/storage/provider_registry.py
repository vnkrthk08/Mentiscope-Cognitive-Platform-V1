from typing import Dict, Type
from app.infrastructure.media.storage.providers.base_provider import StorageProvider
from app.infrastructure.media.storage.providers.s3_provider import S3StorageProvider
from app.infrastructure.media.storage.providers.azure_provider import AzureBlobStorageProvider
from app.infrastructure.media.storage.providers.minio_provider import MinIOStorageProvider
from app.core.config import settings


class StorageProviderRegistry:
    """Registry coordinating active StorageProvider implementations and resolving target engines."""

    def __init__(self):
        self._providers: Dict[str, StorageProvider] = {}
        # Pre-register built-in providers
        self.register("s3", S3StorageProvider())
        self.register("azure", AzureBlobStorageProvider())
        self.register("minio", MinIOStorageProvider())

    def register(self, name: str, provider: StorageProvider) -> None:
        self._providers[name.lower()] = provider

    def get_provider(self, name: str) -> StorageProvider:
        prov = self._providers.get(name.lower())
        if not prov:
            raise ValueError(f"Storage provider '{name}' is not registered.")
        return prov

    def get_default_provider(self) -> StorageProvider:
        # Fallback to minio or config default
        provider_name = os.getenv("STORAGE_PROVIDER", "minio")
        return self.get_provider(provider_name)


import os
# Global registry instance
storage_registry = StorageProviderRegistry()
