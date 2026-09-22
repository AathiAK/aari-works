"""
SQLAlchemy engine, session factory, and declarative base.

Anything that needs a database session — a route, a service, a script —
depends on get_db() rather than constructing its own session, so every
request gets a properly opened-and-closed session.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class every ORM model inherits from."""
    pass


def get_db():
    """FastAPI dependency (used starting Phase 5) that yields a DB session
    and guarantees it's closed even if the request raises an exception."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
