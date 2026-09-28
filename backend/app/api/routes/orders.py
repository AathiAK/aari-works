"""
Order routes.

Customers see only their own orders. Admins may fetch any single order
by id; the admin order list/status update live in /api/admin (Phase 12).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.order import OrderCreate, OrderListResponse, OrderOut, OrderTrackingOut
from app.services.address_service import AddressNotFoundError
from app.services.checkout_service import CartHasUnavailableItemsError, EmptyCartError
from app.services.order_service import (
    OrderNotFoundError,
    create_order,
    get_order,
    get_order_tracking,
    list_orders,
)

router = APIRouter(prefix="/api/orders", tags=["orders"])


def _owner_filter(user: User) -> int | None:
    """None = no ownership restriction (admins)."""
    return None if user.role == "ADMIN" else user.id


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def place_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_order(db, current_user.id, payload)
    except AddressNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    except EmptyCartError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cart is empty")
    except CartHasUnavailableItemsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Some cart items are no longer available in the requested quantity",
        )


@router.get("", response_model=OrderListResponse)
def my_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_orders(db, current_user.id, page, page_size)


@router.get("/{order_id}", response_model=OrderOut)
def order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_order(db, order_id, _owner_filter(current_user))
    except OrderNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")


@router.get("/{order_id}/tracking", response_model=OrderTrackingOut)
def order_tracking(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_order_tracking(db, order_id, _owner_filter(current_user))
    except OrderNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
