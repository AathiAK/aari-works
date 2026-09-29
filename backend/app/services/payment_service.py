"""
Payment business logic.

Every payment status change goes through _apply_status(), which is the
only place that decides what happens to the order and to stock. Callers:
  - create_payment()          (immediate provider result)
  - apply_payment_result()    (simulate route now; webhook / admin refund later)

Lock order is always: order row first, then payment row. Keeping it
consistent means concurrent requests can't deadlock.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Order, Payment, Product
from app.schemas.payment import PaymentCreate
from app.services.order_service import OrderNotFoundError, record_status
from app.services.payment_gateway import get_payment_gateway

logger = logging.getLogger("aari_works.payments")

# from-status -> statuses it may move to. Anything else is rejected.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "PENDING": {"SUCCESS", "FAILED", "CANCELLED"},
    "SUCCESS": {"REFUNDED"},
}

# An order can start (or restart) a payment only from these statuses.
PAYABLE_ORDER_STATUSES = ("PENDING", "PAYMENT_FAILED")


class PaymentNotFoundError(Exception):
    pass


class OrderNotPayableError(Exception):
    pass


class StockUnavailableError(Exception):
    pass


class InvalidPaymentTransitionError(Exception):
    pass


class SimulationNotAllowedError(Exception):
    pass


# --------------------------------------------------------------------------
# Stock helpers (callers hold the transaction; these never commit)
# --------------------------------------------------------------------------

def _lock_products(db: Session, product_ids: list[int]) -> dict[int, Product]:
    rows = (
        db.query(Product)
        .filter(Product.id.in_(product_ids))
        .order_by(Product.id)
        .populate_existing()
        .with_for_update()
        .all()
    )
    return {p.id: p for p in rows}


def _release_stock(db: Session, order: Order) -> None:
    products = _lock_products(db, [i.product_id for i in order.items])
    for item in order.items:
        products[item.product_id].stock_quantity += item.quantity


def _reserve_stock(db: Session, order: Order) -> None:
    products = _lock_products(db, [i.product_id for i in order.items])
    for item in order.items:
        product = products[item.product_id]
        if not product.is_active or product.stock_quantity < item.quantity:
            raise StockUnavailableError()
    for item in order.items:
        products[item.product_id].stock_quantity -= item.quantity


# --------------------------------------------------------------------------
# Locking helpers
# --------------------------------------------------------------------------

def _lock_order(db: Session, order_id: int, user_id: int | None) -> Order:
    query = db.query(Order).filter(Order.id == order_id)
    if user_id is not None:
        query = query.filter(Order.user_id == user_id)
    order = query.populate_existing().with_for_update().first()
    if order is None:
        raise OrderNotFoundError()
    return order


# --------------------------------------------------------------------------
# The one place payment state changes are applied
# --------------------------------------------------------------------------

def _apply_status(
    db: Session,
    order: Order,
    payment: Payment,
    new_status: str,
    comment: str | None = None,
) -> bool:
    """Apply a payment status change plus its order/stock side effects.
    Returns False if it was a repeat (no-op). Does not commit."""
    if payment.status == new_status:
        return False  # idempotent: same result delivered twice

    if new_status not in ALLOWED_TRANSITIONS.get(payment.status, set()):
        raise InvalidPaymentTransitionError(f"{payment.status} -> {new_status}")

    payment.status = new_status

    if new_status == "SUCCESS":
        payment.payment_date = datetime.now(timezone.utc)
        record_status(order, "CONFIRMED", comment or "Payment received")
    elif new_status == "FAILED":
        _release_stock(db, order)
        record_status(order, "PAYMENT_FAILED", comment or "Payment failed")
    elif new_status == "CANCELLED":
        _release_stock(db, order)
        record_status(order, "CANCELLED", comment or "Payment cancelled")
    elif new_status == "REFUNDED":
        record_status(order, "REFUNDED", comment or "Payment refunded")

    logger.info(
        "payment_status_changed order=%s payment=%s txn=%s status=%s",
        order.order_number, payment.id, payment.transaction_id, new_status,
    )
    return True


# --------------------------------------------------------------------------
# Public operations
# --------------------------------------------------------------------------

def create_payment(db: Session, user_id: int, payload: PaymentCreate) -> tuple[Payment, bool]:
    """Start a payment for the customer's order.
    Returns (payment, created). created=False means an existing PENDING or
    SUCCESS payment was returned unchanged (idempotent replay)."""
    try:
        order = _lock_order(db, payload.order_id, user_id)  # ownership + lock
        payment = db.query(Payment).filter(Payment.order_id == order.id).first()

        if payment is not None and payment.status in ("PENDING", "SUCCESS"):
            return payment, False

        if order.status not in PAYABLE_ORDER_STATUSES:
            raise OrderNotPayableError()

        if order.status == "PAYMENT_FAILED":
            _reserve_stock(db, order)  # a failed attempt released it

        gateway = get_payment_gateway()
        result = gateway.create_payment(
            order_number=order.order_number,
            amount=order.total_amount,  # always from the order, never the client
            currency=settings.payment_currency,
            mock_outcome=payload.mock_outcome,
        )

        if payment is None:
            payment = Payment(
                order_id=order.id,
                payment_provider=gateway.name,
                transaction_id=result.transaction_id,
                amount=order.total_amount,
                currency=settings.payment_currency,
                status="PENDING",
            )
            db.add(payment)
            comment = "Payment initiated"
        else:
            # Retry after a failure: reuse the row (order_id is UNIQUE)
            logger.info(
                "payment_retry order=%s old_txn=%s new_txn=%s",
                order.order_number, payment.transaction_id, result.transaction_id,
            )
            payment.payment_provider = gateway.name
            payment.transaction_id = result.transaction_id
            payment.amount = order.total_amount
            payment.currency = settings.payment_currency
            payment.status = "PENDING"
            payment.payment_date = None
            comment = "Payment retry initiated"

        record_status(order, "PAYMENT_PENDING", comment)

        if result.status != "PENDING":
            _apply_status(db, order, payment, result.status)

        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(payment)
    return payment, True


def get_payment(db: Session, payment_id: int, user_id: int | None = None) -> Payment:
    """user_id=None means no ownership filter (admin access)."""
    query = db.query(Payment).filter(Payment.id == payment_id)
    if user_id is not None:
        query = query.join(Order, Order.id == Payment.order_id).filter(Order.user_id == user_id)
    payment = query.first()
    if payment is None:
        raise PaymentNotFoundError()
    return payment


def apply_payment_result(
    db: Session, payment_id: int, new_status: str, comment: str | None = None
) -> Payment:
    """Apply a provider-reported result to an existing payment.
    No ownership check: callers (webhook, admin, simulate) do their own."""
    try:
        first_look = db.get(Payment, payment_id)
        if first_look is None:
            raise PaymentNotFoundError()

        order = _lock_order(db, first_look.order_id, None)
        payment = (
            db.query(Payment)
            .filter(Payment.id == payment_id)
            .populate_existing()
            .with_for_update()
            .one()
        )
        _apply_status(db, order, payment, new_status, comment)
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(payment)
    return payment


def simulate_payment_result(
    db: Session, payment_id: int, outcome: str, user_id: int | None = None
) -> Payment:
    """Mock-only stand-in for the provider webhook."""
    if settings.payment_provider.strip().lower() != "mock":
        raise SimulationNotAllowedError()

    payment = get_payment(db, payment_id, user_id)  # ownership check
    if payment.payment_provider != "mock":
        raise SimulationNotAllowedError()

    return apply_payment_result(db, payment_id, outcome, f"Simulated payment result: {outcome}")
