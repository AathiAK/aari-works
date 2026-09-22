"""
Password hashing and JWT creation/verification.

This is the only module that imports passlib or jose directly — every
other module works with plain strings (raw password, encoded token) and
calls into these functions rather than handling crypto itself.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(subject: str, role: str, expires_minutes: int | None = None) -> str:
    """subject is the user's id (as a string, per JWT 'sub' convention)."""
    expire_minutes = expires_minutes if expires_minutes is not None else settings.jwt_access_token_expire_minutes
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode: dict[str, Any] = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
