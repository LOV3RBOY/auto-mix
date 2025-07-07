# Dockerfile for services/job-orchestrator/

# --- Stage 1: Builder ---
# This stage builds the dependencies for the orchestrator
FROM python:3.9-slim-buster AS builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies needed for psycopg2 (PostgreSQL client)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

# --- Stage 2: Runtime ---
FROM python:3.9-slim-buster

WORKDIR /usr/src/app

# Create non-root user
RUN addgroup --system app && adduser --system --group app

# Install runtime dependencies for psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy pre-built wheels
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .

# Install the Python packages
RUN pip install --no-cache /wheels/*

# Copy the application source code
COPY . .

RUN chown -R app:app /usr/src/app
USER app

EXPOSE 8000

# Default command is to run the API server.
# The 'worker' service in docker-compose.yml will override this command
# to run the Celery worker instead.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
