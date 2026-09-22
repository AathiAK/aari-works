"""
Registration and authentication business logic.

Kept separate from app/api/routes/auth.py so it can be unit tested
without spinning up FastAPI, and so route handlers stay thin (parse
request -> call service -> map result/exception to an HTTP response).
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.db.models import User
from app.schemas.user import UserRegister


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def register_user(db: Session, payload: UserRegister) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise EmailAlreadyRegisteredError()

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        phone=payload.phone,
        role="CUSTOMER",
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # Handles a race: two simultaneous registrations with the same
        # email, both passing the .first() check above before either commits.
        db.rollback()
        raise EmailAlreadyRegisteredError()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError()
    if not user.is_active:
        raise InvalidCredentialsError()
    return user
