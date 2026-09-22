"""Pydantic schemas for the shopping cart."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    unit_price: Decimal
    quantity: int
    line_total: Decimal
    image_url: str | None
    in_stock: bool


class CartOut(BaseModel):
    items: list[CartItemOut]
    subtotal: Decimal
    item_count: int
