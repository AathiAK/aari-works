"""Address business logic. All operations are scoped to a single user."""

from sqlalchemy.orm import Session

from app.db.models import Address, Order
from app.schemas.address import AddressCreate, AddressUpdate


class AddressNotFoundError(Exception):
    pass


class AddressInUseError(Exception):
    """The address is attached to an existing order. Orders reference the
    address row directly (no snapshot), so changing or deleting it would
    rewrite order history."""


def list_addresses(db: Session, user_id: int) -> list[Address]:
    return db.query(Address).filter(Address.user_id == user_id).order_by(Address.created_at.desc()).all()


def get_address(db: Session, user_id: int, address_id: int) -> Address:
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == user_id).first()
    if address is None:
        raise AddressNotFoundError()
    return address


def _is_used_by_order(db: Session, address_id: int) -> bool:
    return db.query(Order.id).filter(Order.address_id == address_id).first() is not None


def create_address(db: Session, user_id: int, payload: AddressCreate) -> Address:
    address = Address(user_id=user_id, **payload.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


def update_address(db: Session, user_id: int, address_id: int, payload: AddressUpdate) -> Address:
    address = get_address(db, user_id, address_id)
    if _is_used_by_order(db, address_id):
        raise AddressInUseError()
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(address, field, value)
    db.commit()
    db.refresh(address)
    return address


def delete_address(db: Session, user_id: int, address_id: int) -> None:
    address = get_address(db, user_id, address_id)
    if _is_used_by_order(db, address_id):
        raise AddressInUseError()
    db.delete(address)
    db.commit()
