"""Pydantic schemas for the checkout pricing preview."""

from decimal import Decimal

from pydantic import BaseModel

from app.schemas.address import AddressOut
from app.schemas.cart import CartItemOut


class CheckoutPreview(BaseModel):
    items: list[CartItemOut]
    address: AddressOut
    subtotal: Decimal
    shipping_amount: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
