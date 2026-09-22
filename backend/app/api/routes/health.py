"""
Health check endpoints.

/health     - liveness: is the FastAPI process up at all.
/health/db  - readiness: can we actually reach PostgreSQL right now.

Docker healthchecks (Phase 16+) and load balancer / EC2 monitoring
(much later, AWS phase) both depend on these existing and being accurate.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ok", "database": "connected"}
