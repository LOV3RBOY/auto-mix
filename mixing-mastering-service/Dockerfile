# Dockerfile for services/mixing-mastering/

# --- Stage 1: Builder ---
FROM python:3.9-slim-buster AS builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# pedalboard may require build-essential for compilation
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

# --- Stage 2: Runtime ---
FROM python:3.9-slim-buster

WORKDIR /usr/src/app

# Create a shared volume mount point for stems
# The actual volume is mounted via docker-compose
RUN mkdir -p /stems

RUN addgroup --system app && adduser --system --group app

# Install runtime system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

# Copy pre-built wheels
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .

# Install dependencies
RUN pip install --no-cache /wheels/*

# Copy application source code
COPY . .

# Change ownership of app and shared volume mount point
RUN chown -R app:app /usr/src/app && chown -R app:app /stems
USER app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
