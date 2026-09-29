"""Pydantic schemas for payments. No card data anywhere, by design."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict


class PaymentCreate(BaseModel):
    order_id: int
    # Honoured ONLY by the mock provider, to let you test each outcome
    # locally. Real providers ignore it. Defaults to SUCCESS when omitted.
    mock_outcome: Literal["SUCCESS", "FAILED", "PENDING"] | None = None


class PaymentSimulate(BaseModel):
    """Mock-only: resolves a PENDING payment, standing in for the provider
    webhook that a real gateway would send."""
    outcome: Literal["SUCCESS", "FAILED", "CANCELLED"]


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    payment_provider: str
    transaction_id: str
    amount: Decimal
    currency: str
    status: str
    payment_date: datetime | None
    created_at: datetime
