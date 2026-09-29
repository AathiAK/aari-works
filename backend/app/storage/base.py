"""
Image storage abstraction.

Every module that needs to store or remove a product image depends on
this interface (obtained via storage.factory.get_image_storage()), never
on a concrete implementation. This is what lets Phase 25 introduce
S3ImageStorage with zero changes to routes, services, or the frontend —
only factory.py gains one more branch.
"""

from abc import ABC, abstractmethod


class ImageStorageService(ABC):
    @abstractmethod
    def save(self, *, data: bytes, filename: str, subfolder: str) -> str:
        """Persist the given bytes under subfolder/filename and return a
        URL path the frontend can use directly, e.g. '/uploads/products/xyz.jpg'."""

    @abstractmethod
    def delete(self, url_path: str) -> None:
        """Remove a previously saved file, given the URL path save() returned.
        Must not raise if the file is already gone."""
