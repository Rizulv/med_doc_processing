"""
Storage factory - automatically selects local or S3 storage based on configuration
"""
from app.config import settings

# Import storage backends
from app.services.storage_local import LocalStorage
from app.services.storage_s3 import S3Storage


def get_storage():
    """
    Get storage backend based on configuration
    
    Returns:
        Storage instance (LocalStorage or S3Storage)
    """
    if settings.storage_backend == "s3":
        return S3Storage(
            bucket_name=settings.s3_bucket_name,
            region=settings.aws_region
        )
    else:
        return LocalStorage(base_path=settings.storage_dir)


# Global storage instance
storage = get_storage()
