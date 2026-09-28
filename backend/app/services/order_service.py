"""
Order business logic: placing orders, listing, detail and tracking.

create_order() is the only place stock is reserved (decremented). It runs
inside a single transaction with the affected product rows locked, so
concurrent checkouts can never oversell a product.
"""

import secrets
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.db.models import CartItem, Order, OrderItem, OrderStatusHistory, Product
from app.schemas.order import (
    OrderCreate,
    OrderListResponse,
    OrderOut,
    OrderTrackingOut,
)
from app.services.address_service import get_address
from app.services.cart_service import get_cart
from app.services.checkout_service import (
    CartHasUnavailableItemsError,
    EmptyCartError,
    compute_pricing,
)

# Every status an order can have. Phase 12 validates admin updates against this.
ORDER_STATUSES = (
    "PENDING",
    "PAYMENT_PENDING",
    "CONFIRMED",
    "PROCESSING",
    "PACKED",
    "SHIPPED",
    "OUT_FOR_DELIVERY",
    "DELIVERED",
    "CANCELLED",
    "PAYMENT_FAILED",
    "RETURN_REQUESTED",
    "RETURNED",
    "REFUNDED",
)

INITIAL_STATUS = "PENDING"


class OrderNotFoundError(Exception):
    pass


def _generate_order_number(db: Session) -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    for _ in range(5):
        candidate = f"AW-{today}-{secrets.token_hex(3).upper()}"
        exists = db.query(Order.id).filter(Order.order_number == candidate).first()
        if exists is None:
            return candidate
    raise RuntimeError("Could not generate a unique order number")


def record_status(order: Order, status: str, comment: str | None = None) -> None:
    """Set the order's current status AND append a history row, always
    together, so the timeline can never drift from the current status.
    Used here now, and by payments/admin in Phases 11-12."""
    order.status = status
    order.status_history.append(OrderStatusHistory(status=status, comment=comment))


def load_order(db: Session, order_id: int, user_id: int | None = None) -> Order:
    """Load an order with everything needed for display.
    user_id=None means 'no ownership filter' (admin access)."""
    query = (
        db.query(Order)
        .options(
            selectinload(Order.items),
            selectinload(Order.status_history),
            joinedload(Order.address),
            joinedload(Order.payment),
        )
        .filter(Order.id == order_id)
    )
    if user_id is not None:
        query = query.filter(Order.user_id == user_id)
    order = query.first()
    if order is None:
        raise OrderNotFoundError()
    return order


def _to_order_out(order: Order) -> OrderOut:
    out = OrderOut.model_validate(order)
    # Sort by id, not created_at: rows written in one transaction share
    # the same database timestamp.
    out.items.sort(key=lambda i: i.id)
    out.status_history.sort(key=lambda h: h.id)
    return out


def create_order(db: Session, user_id: int, payload: OrderCreate) -> OrderOut:
    address = get_address(db, user_id, payload.address_id)  # ownership check

    product_ids = [
        pid
        for (pid,) in db.query(CartItem.product_id)
        .filter(CartItem.user_id == user_id)
        .order_by(CartItem.product_id)
        .all()
    ]
    if not product_ids:
        raise EmptyCartError()

    # Lock product rows (in id order, to avoid deadlocks). populate_existing
    # guarantees we see the freshest stock values, not cached ones.
    locked = (
        db.query(Product)
        .filter(Product.id.in_(product_ids))
        .order_by(Product.id)
        .populate_existing()
        .with_for_update()
        .all()
    )
    products = {p.id: p for p in locked}

    # Read the cart AFTER locking: if a concurrent request just consumed
    # it, we see it empty here and fail cleanly instead of double-ordering.
    cart = get_cart(db, user_id)
    pricing = compute_pricing(cart)  # raises EmptyCartError / CartHasUnavailableItemsError

    order = Order(
        user_id=user_id,
        address_id=address.id,
        order_number=_generate_order_number(db),
        subtotal=pricing["subtotal"],
        shipping_amount=pricing["shipping_amount"],
        tax_amount=pricing["tax_amount"],
        discount_amount=pricing["discount_amount"],
        total_amount=pricing["total_amount"],
        status=INITIAL_STATUS,
    )
    db.add(order)

    for item in cart.items:
        order.items.append(
            OrderItem(
                product_id=item.product_id,
                product_name=item.product_name,  # snapshot
                quantity=item.quantity,
                unit_price=item.unit_price,      # snapshot
                total_price=item.line_total,
            )
        )
        products[item.product_id].stock_quantity -= item.quantity

    db.query(CartItem).filter(CartItem.user_id == user_id).delete(synchronize_session=False)

    order.status_history.append(OrderStatusHistory(status=INITIAL_STATUS, comment="Order placed"))

    try:
        db.commit()
    except IntegrityError:
        # e.g. the stock >= 0 CHECK constraint as a last line of defence
        db.rollback()
        raise CartHasUnavailableItemsError()

    return _to_order_out(load_order(db, order.id, user_id))


def list_orders(db: Session, user_id: int, page: int = 1, page_size: int = 20) -> OrderListResponse:
    query = db.query(Order).filter(Order.user_id == user_id)
    total = query.count()
    items = (
        query.order_by(Order.created_at.desc(), Order.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return OrderListResponse(items=items, total=total, page=page, page_size=page_size)


def get_order(db: Session, order_id: int, user_id: int | None = None) -> OrderOut:
    return _to_order_out(load_order(db, order_id, user_id))


def get_order_tracking(db: Session, order_id: int, user_id: int | None = None) -> OrderTrackingOut:
    order = _to_order_out(load_order(db, order_id, user_id))
    return OrderTrackingOut(
        order_number=order.order_number,
        status=order.status,
        timeline=order.status_history,
    )
