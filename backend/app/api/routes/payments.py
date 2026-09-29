"""
Payment routes.

Customers can pay only their own orders. Admins may read any payment.
Card details never pass through these routes.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.payment import PaymentCreate, PaymentOut, PaymentSimulate
from app.services.order_service import OrderNotFoundError
from app.services.payment_gateway import PaymentGatewayError
from app.services.payment_service import (
    InvalidPaymentTransitionError,
    OrderNotPayableError,
    PaymentNotFoundError,
    SimulationNotAllowedError,
    StockUnavailableError,
    create_payment,
    get_payment,
    simulate_payment_result,
)

logger = logging.getLogger("aari_works.payments")

router = APIRouter(prefix="/api/payments", tags=["payments"])


def _owner_filter(user: User) -> int | None:
    """None = no ownership restriction (admins)."""
    return None if user.role == "ADMIN" else user.id


@router.post("/create", response_model=PaymentOut)
def create(
    payload: PaymentCreate,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """201 = new payment started. 200 = an existing PENDING/SUCCESS payment
    for this order was returned (safe to call repeatedly)."""
    try:
        payment, created = create_payment(db, current_user.id, payload)
    except OrderNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    except OrderNotPayableError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This order can't be paid in its current state",
        )
    except StockUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Some items in this order are no longer available",
        )
    except PaymentGatewayError:
        logger.exception("Payment gateway error")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Payment provider unavailable, please try again",
        )

    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return payment


@router.get("/{payment_id}", response_model=PaymentOut)
def payment_detail(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_payment(db, payment_id, _owner_filter(current_user))
    except PaymentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")


@router.post("/{payment_id}/simulate", response_model=PaymentOut)
def simulate(
    payment_id: int,
    payload: PaymentSimulate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """MOCK ONLY: resolves a PENDING payment. Replaced by a signed provider
    webhook when a real gateway is added."""
    try:
        return simulate_payment_result(db, payment_id, payload.outcome, _owner_filter(current_user))
    except PaymentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    except SimulationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Payment simulation is only available with the mock provider",
        )
    except InvalidPaymentTransitionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This payment can't move to that status from its current one",
        )
