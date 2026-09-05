from typing import Dict, Any
from app.infrastructure.media.storage.providers.base_provider import StorageProvider


class MinIOStorageProvider(StorageProvider):
    """Local development implementation of S3-compatible MinIO object storage."""

    def __init__(self, endpoint: str = "http://localhost:9000", access_key: str = "", secret_key: str = ""):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key

    async def generate_upload_url(self, bucket_name: str, object_key: str, expires_in: int = 3600) -> str:
        return f"{self.endpoint}/{bucket_name}/{object_key}?AWSAccessKeyId=MINIO_KEY&Expires=1784732984&Signature=minio_sig"

    async def generate_download_url(self, bucket_name: str, object_key: str, expires_in: int = 3600) -> str:
        return f"{self.endpoint}/{bucket_name}/{object_key}?AWSAccessKeyId=MINIO_KEY&Expires=1784732984&Signature=minio_sig"

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
            "etag": "minio_etag_mock",
        }
