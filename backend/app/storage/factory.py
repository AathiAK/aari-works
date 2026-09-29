"""
Selects the active ImageStorageService based on IMAGE_STORAGE.

This is the ONLY file that needs a new branch when S3 support is added
in Phase 25. Everything that calls get_image_storage() is unaffected.
"""

from app.core.config import settings
from app.storage.base import ImageStorageService
from app.storage.local import LocalImageStorage


def get_image_storage() -> ImageStorageService:
    mode = settings.image_storage.strip().lower()
    if mode == "local":
        return LocalImageStorage()
    if mode == "s3":
        raise NotImplementedError(
            "IMAGE_STORAGE=s3 is not implemented until Phase 25 (AWS deployment phase)."
        )
    raise ValueError(f"Unknown IMAGE_STORAGE value: '{settings.image_storage}'")
