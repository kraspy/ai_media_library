########################################
# Builder stage: build wheels (all deps)
########################################
FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1

# Build dependencies for Python packages that need compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

# Copy metadata first to leverage Docker cache when deps don't change
COPY pyproject.toml poetry.lock* /src/
# Copy project sources
COPY . /src

# Build wheels for the project and dependencies into /wheels
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip wheel . --wheel-dir /wheels

########################################
# Runtime stage: minimal image
########################################
FROM python:3.11-slim AS runner

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    PATH=$APP_HOME/.venv/bin:$PATH

# Non-root user for security
RUN addgroup --system app && adduser --system --group app

WORKDIR /app

# Install minimal system libs needed at runtime (e.g. libpq for psycopg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder and install them without touching the network
COPY --from=builder /wheels /wheels
RUN python -m pip install --upgrade pip \
    && pip install --no-index --find-links /wheels /wheels/*.whl

# Copy source code (already built in the wheels) — keeps app in /app for convenience
COPY --from=builder /src /app

# Fix permissions and switch to non-root user
RUN chown -R app:app /app
USER app

EXPOSE 8000

# Default entrypoint: use START_COMMAND env var to override (for example to run gunicorn/uvicorn)
CMD sh -c 'exec ${START_COMMAND:-uvicorn app.main:app --host 0.0.0.0 --port 8000}'
