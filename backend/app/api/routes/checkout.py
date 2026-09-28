"""
Checkout preview route.

This does NOT create an order — it's a read-only pricing preview so the
frontend can show the customer a confirmation screen before they commit.
Actual order creation (which re-runs this same pricing logic) is Phase 10.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.checkout import CheckoutPreview
from app.services.address_service import AddressNotFoundError
from app.services.checkout_service import (
    CartHasUnavailableItemsError,
    EmptyCartError,
    preview_checkout,
)

router = APIRouter(prefix="/api/checkout", tags=["checkout"])


@router.get("/preview", response_model=CheckoutPreview)
def get_checkout_preview(
    address_id: int = Query(..., description="Address the order would ship to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return preview_checkout(db, current_user.id, address_id)
    except AddressNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    except EmptyCartError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cart is empty")
    except CartHasUnavailableItemsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Some cart items are no longer available in the requested quantity",
        )
