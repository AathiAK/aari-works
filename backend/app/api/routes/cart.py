"""Shopping cart routes. All require an authenticated customer."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartOut
from app.services.cart_service import (
    CartItemNotFoundError,
    InsufficientStockError,
    ProductInactiveError,
    ProductNotFoundError,
    add_item,
    get_cart,
    remove_item,
    update_item,
)

router = APIRouter(prefix="/api/cart", tags=["cart"])


@router.get("", response_model=CartOut)
def view_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_cart(db, current_user.id)


@router.post("/items", response_model=CartOut, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    payload: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return add_item(db, current_user.id, payload)
    except ProductNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    except ProductInactiveError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product is not available")
    except InsufficientStockError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Not enough stock available")


@router.put("/items/{cart_item_id}", response_model=CartOut)
def update_cart_item(
    cart_item_id: int,
    payload: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return update_item(db, current_user.id, cart_item_id, payload)
    except CartItemNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    except InsufficientStockError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Not enough stock available")


@router.delete("/items/{cart_item_id}", response_model=CartOut)
def remove_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return remove_item(db, current_user.id, cart_item_id)
    except CartItemNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
