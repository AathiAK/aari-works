"""Address routes. All require authentication; scoped to the current user."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.address import AddressCreate, AddressOut, AddressUpdate
from app.services.address_service import (
    AddressInUseError,
    AddressNotFoundError,
    create_address,
    delete_address,
    list_addresses,
    update_address,
)

router = APIRouter(prefix="/api/addresses", tags=["addresses"])

IN_USE_MESSAGE = (
    "This address is used by an existing order and can't be changed or deleted. "
    "Please create a new address instead."
)


@router.get("", response_model=list[AddressOut])
def get_addresses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_addresses(db, current_user.id)


@router.post("", response_model=AddressOut, status_code=status.HTTP_201_CREATED)
def create(
    payload: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_address(db, current_user.id, payload)


@router.put("/{address_id}", response_model=AddressOut)
def update(
    address_id: int,
    payload: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return update_address(db, current_user.id, address_id, payload)
    except AddressNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    except AddressInUseError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=IN_USE_MESSAGE)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        delete_address(db, current_user.id, address_id)
    except AddressNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    except AddressInUseError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=IN_USE_MESSAGE)
