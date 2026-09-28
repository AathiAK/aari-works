"""Pydantic schemas for customer addresses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AddressCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    phone: str = Field(min_length=1, max_length=20)
    address_line1: str = Field(min_length=1, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    postal_code: str = Field(min_length=1, max_length=20)
    country: str = Field(default="India", max_length=100)


class AddressUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=150)
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    address_line1: str | None = Field(default=None, min_length=1, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = Field(default=None, min_length=1, max_length=100)
    postal_code: str | None = Field(default=None, min_length=1, max_length=20)
    country: str | None = Field(default=None, max_length=100)


class AddressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    phone: str
    address_line1: str
    address_line2: str | None
    city: str
    state: str
    postal_code: str
    country: str
    created_at: datetime
    updated_at: datetime
