"""
Local filesystem image storage.

Used when IMAGE_STORAGE=local (the default, and the only mode used until
Phase 25). Files are written under settings.local_upload_dir, which in
Docker (Phase 17 onward) is the uploads_data volume mount point.
"""

import os

from app.core.config import settings
from app.storage.base import ImageStorageService

UPLOADS_URL_PREFIX = "/uploads"


class LocalImageStorage(ImageStorageService):
    def save(self, *, data: bytes, filename: str, subfolder: str) -> str:
        target_dir = os.path.join(settings.local_upload_dir, subfolder)
        os.makedirs(target_dir, exist_ok=True)

        target_path = os.path.join(target_dir, filename)
        with open(target_path, "wb") as f:
            f.write(data)

        return f"{UPLOADS_URL_PREFIX}/{subfolder}/{filename}"

    def delete(self, url_path: str) -> None:
        if not url_path.startswith(f"{UPLOADS_URL_PREFIX}/"):
            return  # not a local-storage path (e.g. leftover S3 URL) — nothing to do here
        relative = url_path[len(f"{UPLOADS_URL_PREFIX}/"):]
        full_path = os.path.join(settings.local_upload_dir, relative)
        try:
            os.remove(full_path)
        except FileNotFoundError:
            pass  # already gone — deleting an already-deleted file is not an error
