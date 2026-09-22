# Aari Works Backend

FastAPI backend for the Aari Works e-commerce application.

## Local development (standalone, outside Docker)
\`\`\`bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
\`\`\`

Normally, though, this backend runs inside Docker Compose — see the root README.

## Structure
- `app/core/` — configuration, security (JWT/password hashing), shared dependencies
- `app/db/` — SQLAlchemy engine/session setup and models
- `app/schemas/` — Pydantic request/response models
- `app/api/routes/` — FastAPI route handlers
- `app/services/` — business logic
- `app/storage/` — image storage abstraction (local disk / S3)
- `app/utils/` — helper scripts (e.g., admin user creation)
- `alembic/` — database migrations
- `tests/` — pytest test suite
