"""
Payment provider abstraction.

The rest of the app only knows the PaymentGateway interface. To add a
real provider (Razorpay, Stripe...):
  1. Subclass PaymentGateway and implement create_payment() by calling the
     provider's API with the order number, amount and currency. Return its
     payment/order id as transaction_id and status "PENDING".
  2. Add it to get_payment_gateway() under a new PAYMENT_PROVIDER value.
  3. Add a signature-verified webhook route that calls
     payment_service.apply_payment_result() with the outcome.
No other file changes.

Card numbers, CVV and PINs never reach this application. The customer
enters them on the provider's hosted checkout.
"""

import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from app.core.config import settings


class PaymentGatewayError(Exception):
    """The provider is misconfigured, unreachable or rejected the request."""


@dataclass(frozen=True)
class GatewayPaymentResult:
    transaction_id: str
    status: str  # "PENDING" | "SUCCESS" | "FAILED"


class PaymentGateway(ABC):
    name: str

    @abstractmethod
    def create_payment(
        self,
        *,
        order_number: str,
        amount: Decimal,
        currency: str,
        mock_outcome: str | None = None,
    ) -> GatewayPaymentResult:
        """Start a payment. mock_outcome is a hint used only by the mock."""


class MockPaymentService(PaymentGateway):
    """Simulates a gateway locally. No network calls, no credentials."""

    name = "mock"
    _OUTCOMES = {"SUCCESS", "FAILED", "PENDING"}

    def create_payment(
        self,
        *,
        order_number: str,
        amount: Decimal,
        currency: str,
        mock_outcome: str | None = None,
    ) -> GatewayPaymentResult:
        outcome = mock_outcome or "SUCCESS"
        if outcome not in self._OUTCOMES:
            raise PaymentGatewayError(f"Unknown mock outcome: {outcome}")
        return GatewayPaymentResult(
            transaction_id=f"mock_txn_{secrets.token_hex(8)}",
            status=outcome,
        )


def get_payment_gateway() -> PaymentGateway:
    provider = settings.payment_provider.strip().lower()
    if provider == "mock":
        return MockPaymentService()
    raise PaymentGatewayError(f"Unsupported PAYMENT_PROVIDER: '{provider}'")
