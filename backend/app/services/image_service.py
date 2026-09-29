"""
Product image upload business logic: validation + orchestration.

Validation deliberately checks the actual decoded image content (via
Pillow), not just the filename extension or the client-supplied
Content-Type header — either of those can be spoofed by renaming an
arbitrary file.
"""

import io
from uuid import uuid4

from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.db.models import Product
from app.storage.base import ImageStorageService

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB

# content-type -> file extension used for the saved filename.
ALLOWED_CONTENT_TYPES: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


class ProductNotFoundError(Exception):
    pass


class UnsupportedFileTypeError(Exception):
    pass


class FileTooLargeError(Exception):
    pass


class InvalidImageContentError(Exception):
    pass


def _validate(content_type: str | None, data: bytes) -> str:
    """Returns the file extension to use, or raises one of the errors above."""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise UnsupportedFileTypeError()

    if len(data) > MAX_UPLOAD_BYTES:
        raise FileTooLargeError()

    if not data:
        raise InvalidImageContentError()

    # Confirm the bytes actually decode as an image of the claimed type —
    # this is what catches a renamed non-image file.
    try:
        with Image.open(io.BytesIO(data)) as img:
            img.verify()
    except UnidentifiedImageError:
        raise InvalidImageContentError()
    except Exception:
        raise InvalidImageContentError()

    return ALLOWED_CONTENT_TYPES[content_type]


def upload_product_image(
    db: Session,
    storage: ImageStorageService,
    product_id: int,
    *,
    content_type: str | None,
    data: bytes,
) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise ProductNotFoundError()

    ext = _validate(content_type, data)

    old_image_url = product.image_url

    filename = f"{uuid4().hex}{ext}"
    new_url = storage.save(data=data, filename=filename, subfolder="products")

    product.image_url = new_url
    db.commit()
    db.refresh(product)

    if old_image_url:
        storage.delete(old_image_url)  # best-effort cleanup, after the DB commit succeeds

    return product
