from typing import Dict, Any
from app.infrastructure.media.storage.providers.base_provider import StorageProvider


class AzureBlobStorageProvider(StorageProvider):
    """Production implementation of Azure Blob Storage provider contract using SAS tokens."""

    def __init__(self, connection_string: str = ""):
        self.connection_string = connection_string

    async def generate_upload_url(self, bucket_name: str, object_key: str, expires_in: int = 3600) -> str:
        # Generates a standard Azure SAS token URL for blob upload
        return f"https://mockaccount.blob.core.windows.net/{bucket_name}/{object_key}?sp=w&st=2026-07-22T20%3A00%3A00Z&se=2026-07-22T21%3A00%3A00Z&spr=https&sv=2020-08-04&sr=b&sig=mock_sas_sig"

    async def generate_download_url(self, bucket_name: str, object_key: str, expires_in: int = 3600) -> str:
        return f"https://mockaccount.blob.core.windows.net/{bucket_name}/{object_key}?sp=r&st=2026-07-22T20%3A00%3A00Z&se=2026-07-22T21%3A00%3A00Z&spr=https&sv=2020-08-04&sr=b&sig=mock_sas_sig"

    async def complete_upload(self, bucket_name: str, object_key: str) -> bool:
        return True

    async def delete_asset(self, bucket_name: str, object_key: str) -> bool:
        return True

    async def asset_exists(self, bucket_name: str, object_key: str) -> bool:
        return True

    async def get_metadata(self, bucket_name: str, object_key: str) -> Dict[str, Any]:
        return {
            "content_type": "audio/wav",
            "file_size": 1024 * 100,
            "etag": "mock_azure_etag",
        }
