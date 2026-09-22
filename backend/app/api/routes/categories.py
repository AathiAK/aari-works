"""Category routes: public read, admin write."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.database import get_db
from app.db.models import User
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services.category_service import (
    CategoryHasProductsError,
    CategoryNameTakenError,
    CategoryNotFoundError,
    create_category,
    delete_category,
    get_category,
    list_categories,
    update_category,
)

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    return list_categories(db)


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        return create_category(db, payload)
    except CategoryNameTakenError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category name already exists")


@router.put("/{category_id}", response_model=CategoryOut)
def update(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        return update_category(db, category_id, payload)
    except CategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    except CategoryNameTakenError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category name already exists")


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    category_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        delete_category(db, category_id)
    except CategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    except CategoryHasProductsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a category that still has products",
        )
