"""Address business logic. All operations are scoped to a single user."""

from sqlalchemy.orm import Session

from app.db.models import Address
from app.schemas.address import AddressCreate, AddressUpdate


class AddressNotFoundError(Exception):
    pass


def list_addresses(db: Session, user_id: int) -> list[Address]:
    return db.query(Address).filter(Address.user_id == user_id).order_by(Address.created_at.desc()).all()


def get_address(db: Session, user_id: int, address_id: int) -> Address:
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == user_id).first()
    if address is None:
        raise AddressNotFoundError()
    return address


def create_address(db: Session, user_id: int, payload: AddressCreate) -> Address:
    address = Address(user_id=user_id, **payload.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


def update_address(db: Session, user_id: int, address_id: int, payload: AddressUpdate) -> Address:
    address = get_address(db, user_id, address_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(address, field, value)
    db.commit()
    db.refresh(address)
    return address


def delete_address(db: Session, user_id: int, address_id: int) -> None:
    address = get_address(db, user_id, address_id)
    db.delete(address)
    db.commit()
