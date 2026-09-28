"""Pydantic schemas for orders, order history and tracking."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.schemas.address import AddressOut


class OrderCreate(BaseModel):
    address_id: int


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class StatusHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    comment: str | None
    created_at: datetime


class PaymentSummaryOut(BaseModel):
    """Non-sensitive payment metadata only. Null on an order until a
    payment is created (Phase 11)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    payment_provider: str
    transaction_id: str
    amount: Decimal
    currency: str
    status: str
    payment_date: datetime | None


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    status: str
    subtotal: Decimal
    shipping_amount: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    address: AddressOut
    items: list[OrderItemOut]
    status_history: list[StatusHistoryOut]
    payment: PaymentSummaryOut | None


class OrderListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    status: str
    total_amount: Decimal
    created_at: datetime


class OrderListResponse(BaseModel):
    items: list[OrderListOut]
    total: int
    page: int
    page_size: int


class OrderTrackingOut(BaseModel):
    order_number: str
    status: str
    timeline: list[StatusHistoryOut]
