"""
Checkout pricing engine.

This is the single source of truth for how a cart becomes a priced
order. Phase 10's order creation calls compute_pricing() directly
rather than reimplementing the math, so the price a customer previews
here is guaranteed to match what they're actually charged.
"""

from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.cart import CartOut
from app.services.address_service import get_address
from app.services.cart_service import get_cart


class EmptyCartError(Exception):
    pass


class CartHasUnavailableItemsError(Exception):
    pass


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def compute_pricing(cart: CartOut, discount_amount: Decimal = Decimal("0.00")) -> dict:
    """Pure calculation — no DB access, so it's trivially unit-testable
    and reusable between the preview endpoint and real order creation."""
    if not cart.items:
        raise EmptyCartError()

    unavailable = [i for i in cart.items if not i.in_stock]
    if unavailable:
        raise CartHasUnavailableItemsError()

    subtotal = cart.subtotal

    if subtotal >= Decimal(str(settings.free_shipping_threshold)):
        shipping_amount = Decimal("0.00")
    else:
        shipping_amount = Decimal(str(settings.shipping_flat_amount))

    tax_amount = _money(subtotal * Decimal(str(settings.tax_rate_percent)) / Decimal("100"))

    total_amount = _money(subtotal + shipping_amount + tax_amount - discount_amount)

    return {
        "subtotal": _money(subtotal),
        "shipping_amount": _money(shipping_amount),
        "tax_amount": tax_amount,
        "discount_amount": _money(discount_amount),
        "total_amount": total_amount,
    }


def preview_checkout(db: Session, user_id: int, address_id: int) -> dict:
    address = get_address(db, user_id, address_id)  # raises AddressNotFoundError if not owned/found
    cart = get_cart(db, user_id)
    pricing = compute_pricing(cart)
    return {
        "items": cart.items,
        "address": address,
        **pricing,
    }
