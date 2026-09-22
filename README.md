# Aari Works — E-Commerce Platform

A small, simple e-commerce web application for an Aari embroidery business,
designed for approximately 50 concurrent users.

## Stack
- **Frontend:** React + Vite + Axios + React Router
- **Backend:** FastAPI + SQLAlchemy + Alembic + Pydantic
- **Database:** PostgreSQL 16
- **Reverse proxy:** Nginx
- **Local image storage:** Docker volume (swapped for Amazon S3 only during AWS deployment)
- **Containerization:** Docker + Docker Compose

## Development Philosophy
This project is built entirely **locally first**. AWS is not required, referenced,
or configured until the AWS deployment phase. See `/docs` (added later) or the
project changelog for the phase-by-phase build order.

## Quick Start
See detailed setup instructions in later phases. Summary:

\`\`\`bash
git clone <repo-url>
cd aari-works
cp .env.example .env
docker compose build
docker compose up -d
docker compose ps
\`\`\`

## Project Structure
- `backend/` — FastAPI application
- `frontend/` — React + Vite application
- `nginx/` — reverse proxy configuration
- `scripts/` — operational scripts (backup, etc.)

## Status
🚧 Under active incremental development. See project phases for current progress.
