"""
Admin-only routes: customer list, order list/status, refunds.
Every route here requires require_admin.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.database import get_db
from app.db.models import User
from app.schemas.admin import (
    AdminOrderListResponse,
    AdminUserOut,
    OrderStatusUpdate,
    RefundRequest,
)
from app.schemas.order import OrderOut
from app.schemas.payment import PaymentOut
from app.services.admin_service import (
    InvalidOrderTransitionError,
    OrderNotFoundError,
    list_admin_orders,
    list_users,
    update_order_status,
)
from app.services.payment_service import (
    InvalidPaymentTransitionError,
    PaymentNotFoundError,
    apply_payment_result,
    get_payment,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=list[AdminUserOut])
def get_users(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return list_users(db)


@router.get("/orders", response_model=AdminOrderListResponse)
def get_orders(
    status_filter: str | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None, description="Order number or customer email"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return list_admin_orders(db, status=status_filter, search=search, page=page, page_size=page_size)


@router.put("/orders/{order_id}/status", response_model=OrderOut)
def set_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        return update_order_status(db, order_id, payload.status, payload.comment)
    except OrderNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    except InvalidOrderTransitionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This order can't move to that status from its current one. "
                "Paid orders must be cancelled via the refund endpoint instead."
            ),
        )


@router.post("/payments/{payment_id}/refund", response_model=PaymentOut)
def refund_payment(
    payment_id: int,
    payload: RefundRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        get_payment(db, payment_id, None)  # 404 early if it doesn't exist
        return apply_payment_result(
            db, payment_id, "REFUNDED", payload.comment or "Refunded by admin"
        )
    except PaymentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    except InvalidPaymentTransitionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only a successful payment can be refunded",
        )
