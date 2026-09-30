# ---------- Stage 1: build ----------
# Installs dependencies into an isolated location, with the full set of
# build tools available. None of this stage's layers end up in the
# final image — only the installed packages get copied forward.
FROM python:3.12-slim AS builder

WORKDIR /build

# gcc/libpq-dev are needed to build psycopg's C extension and bcrypt's
# native module. Kept only in this stage, never in the runtime image.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Installing into a dedicated prefix (rather than system site-packages)
# lets us copy just this one directory into the runtime stage, without
# dragging along apt caches, gcc, or pip's own metadata.
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------- Stage 2: runtime ----------
# Slim image, no build tools, no apt cache, runs as a non-root user.
FROM python:3.12-slim AS runtime

# libpq5 is the runtime (not dev) Postgres client library — psycopg's
# compiled extension needs it present even though gcc/libpq-dev (the
# build-time versions) are gone.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# A dedicated, unprivileged user. Running as root inside a container is
# a real privilege-escalation risk if the app is ever compromised —
# there's no reason this process needs root.
RUN groupadd --system aari && useradd --system --gid aari --create-home aari

WORKDIR /app

# Bring in only the installed packages from the build stage — no gcc,
# no pip cache, no build artifacts.
COPY --from=builder /install /usr/local

# Application code. Copied after dependencies so that code-only changes
# don't invalidate the (much slower) dependency-install layer above.
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

# The uploads directory is created here so it exists with correct
# ownership even before the uploads_data volume (Phase 17) is mounted
# over it — the volume mount will inherit this directory's presence.
RUN mkdir -p /app/uploads/products && chown -R aari:aari /app

USER aari

EXPOSE 8000

# Docker (and later, EC2 monitoring) uses this to know the container is
# actually serving requests, not just that the process started.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# No --reload: file-watching has no purpose in production and costs
# a small amount of CPU/memory for nothing. Workers=1 is intentional
# for a 50-user app on a t3a.small — see the Phase 20 EC2 sizing note
# for when to reconsider.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
