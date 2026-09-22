"""Product routes: public listing/detail with search, admin write."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.database import get_db
from app.db.models import User
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductOut,
    ProductUpdate,
)
from app.services.product_service import (
    ProductNotFoundError,
    create_product,
    delete_product,
    get_product,
    list_products,
    update_product,
)

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
def get_products(
    search: str | None = Query(default=None, description="Search product name/description"),
    category_id: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = list_products(
        db,
        search=search,
        category_id=category_id,
        active_only=True,
        page=page,
        page_size=page_size,
    )
    return ProductListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{product_id}", response_model=ProductOut)
def get_product_detail(product_id: int, db: Session = Depends(get_db)):
    try:
        return get_product(db, product_id)
    except ProductNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return create_product(db, payload)


@router.put("/{product_id}", response_model=ProductOut)
def update(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        return update_product(db, product_id, payload)
    except ProductNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    product_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        delete_product(db, product_id)
    except ProductNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
