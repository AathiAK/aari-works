"""
Admin business logic: customer/order visibility, order fulfillment
transitions, and refunds.

update_order_status() is the only place that moves an order between
fulfillment statuses. Refunds intentionally reuse
payment_service.apply_payment_result() rather than duplicating the
SUCCESS -> REFUNDED rule that already lives there.
"""

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.db.models import Order, Payment, User
from app.schemas.admin import AdminOrderListItem, AdminOrderListResponse
from app.services.order_service import load_order, record_status, _to_order_out
from app.services.payment_service import (
    _lock_order,
    _release_stock,
)

# from-status -> statuses an admin may set directly via PUT .../status.
# CONFIRMED and beyond deliberately have no direct path to CANCELLED:
# those orders are paid, and must go through the refund endpoint instead,
# so stock/payment state can never silently disagree.
ADMIN_DIRECT_TRANSITIONS: dict[str, set[str]] = {
    "PENDING": {"CANCELLED"},
    "PAYMENT_PENDING": {"CANCELLED"},
    "CONFIRMED": {"PROCESSING"},
    "PROCESSING": {"PACKED"},
    "PACKED": {"SHIPPED"},
    "SHIPPED": {"OUT_FOR_DELIVERY"},
    "OUT_FOR_DELIVERY": {"DELIVERED"},
    "DELIVERED": {"RETURN_REQUESTED"},
    "RETURN_REQUESTED": {"RETURNED"},
}

STOCK_RELEASING_STATUSES = {"CANCELLED"}


class OrderNotFoundError(Exception):
    pass


class InvalidOrderTransitionError(Exception):
    pass


def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.created_at.desc()).all()


def list_admin_orders(
    db: Session,
    *,
    status: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> AdminOrderListResponse:
    query = (
        db.query(Order)
        .join(User, User.id == Order.user_id)
        .outerjoin(Payment, Payment.order_id == Order.id)
        .options(joinedload(Order.user), joinedload(Order.payment))
    )

    if status:
        query = query.filter(Order.status == status)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Order.order_number.ilike(like), User.email.ilike(like)))

    total = query.count()
    orders = (
        query.order_by(Order.created_at.desc(), Order.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [
        AdminOrderListItem(
            id=o.id,
            order_number=o.order_number,
            customer_name=o.user.name,
            customer_email=o.user.email,
            status=o.status,
            payment_status=o.payment.status if o.payment else None,
            total_amount=o.total_amount,
            created_at=o.created_at,
        )
        for o in orders
    ]
    return AdminOrderListResponse(items=items, total=total, page=page, page_size=page_size)


def update_order_status(db: Session, order_id: int, new_status: str, comment: str | None):
    try:
        order = _lock_order(db, order_id, None)  # admin: no ownership filter

        if new_status not in ADMIN_DIRECT_TRANSITIONS.get(order.status, set()):
            raise InvalidOrderTransitionError(f"{order.status} -> {new_status}")

        if new_status in STOCK_RELEASING_STATUSES:
            order = load_order(db, order_id)  # need .items populated for release
            order = _lock_order(db, order_id, None)  # re-lock after the reload
            _release_stock(db, order)

        record_status(order, new_status, comment)
        db.commit()
    except OrderNotFoundError:
        raise
    except Exception:
        db.rollback()
        raise

    return _to_order_out(load_order(db, order_id))
