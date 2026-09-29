"""
Product image upload route. Admin-only.

Kept in its own file (rather than folded into products.py) since it's a
distinct concern (multipart upload, not JSON CRUD) with its own request
shape and error cases.
"""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.database import get_db
from app.db.models import User
from app.schemas.product import ProductOut
from app.services.image_service import (
    FileTooLargeError,
    InvalidImageContentError,
    ProductNotFoundError,
    UnsupportedFileTypeError,
    upload_product_image,
)
from app.services.product_service import get_product
from app.storage.factory import get_image_storage

router = APIRouter(prefix="/api/admin/products", tags=["products"])


@router.post("/{product_id}/image", response_model=ProductOut)
async def upload_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    data = await file.read()
    storage = get_image_storage()

    try:
        upload_product_image(
            db, storage, product_id, content_type=file.content_type, data=data
        )
    except ProductNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    except UnsupportedFileTypeError:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, or WEBP images are allowed",
        )
    except FileTooLargeError:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image must be 5MB or smaller",
        )
    except InvalidImageContentError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File is not a valid image",
        )

    # Reload with category joined, matching the shape every other
    # product endpoint returns.
    return get_product(db, product_id)
