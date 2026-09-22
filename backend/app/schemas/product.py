"""Pydantic schemas for products."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryOut


class ProductCreate(BaseModel):
    category_id: int
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    stock_quantity: int = Field(ge=0, default=0)
    is_active: bool = True


class ProductUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    stock_quantity: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    category: CategoryOut
    name: str
    description: str | None
    price: Decimal
    stock_quantity: int
    image_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductListOut(BaseModel):
    """Lighter shape for list views — omits description to keep listing
    payloads small; full detail is fetched via GET /products/{id}."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    name: str
    price: Decimal
    stock_quantity: int
    image_url: str | None
    is_active: bool


class ProductListResponse(BaseModel):
    items: list[ProductListOut]
    total: int
    page: int
    page_size: int
