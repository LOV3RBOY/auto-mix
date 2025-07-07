# Dockerfile for services/sound-generation/

# --- Stage 1: Builder ---
# A simple builder to pre-compile python packages
FROM python:3.9-slim-buster AS builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

# --- Stage 2: Runtime ---
FROM python:3.9-slim-buster

WORKDIR /usr/src/app

# Create a dedicated directory for generated audio output
RUN mkdir -p /usr/src/app/generated_audio

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

# Copy pre-built wheels from builder
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .

# Install dependencies
RUN pip install --no-cache /wheels/*

# Copy the application source code
COPY . .

# Grant write permissions for the output directory to the app user
# and change ownership of the entire app directory.
RUN chown -R app:app /usr/src/app

# Switch to the non-root user
USER app

# ARG for build-time secrets is an option, but ENV is common for docker-compose
# Ensure STABILITY_AI_API_KEY is set in the environment (e.g., via docker-compose.yml)
ARG STABILITY_AI_API_KEY
ENV STABILITY_AI_API_KEY=${STABILITY_AI_API_KEY}

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
