"""Pydantic schemas for admin-only views."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: str | None
    role: str
    is_active: bool
    created_at: datetime


class AdminOrderListItem(BaseModel):
    id: int
    order_number: str
    customer_name: str
    customer_email: str
    status: str
    payment_status: str | None
    total_amount: Decimal
    created_at: datetime


class AdminOrderListResponse(BaseModel):
    items: list[AdminOrderListItem]
    total: int
    page: int
    page_size: int


class OrderStatusUpdate(BaseModel):
    status: str
    comment: str | None = None


class RefundRequest(BaseModel):
    comment: str | None = None
