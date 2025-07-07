# Dockerfile for services/style-analysis-service/

# --- Stage 1: Builder ---
# Installs system dependencies and Python packages
FROM python:3.9-slim-buster AS builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install libsndfile, a required system dependency for librosa/soundfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

# Install python packages using wheels for faster installation in the final stage
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

# --- Stage 2: Runtime ---
# Creates the final production image
FROM python:3.9-slim-buster

WORKDIR /usr/src/app

# Create a non-root user for security
RUN addgroup --system app && adduser --system --group app

# Install the required system library from the builder stage is not needed as it's a base system package,
# but we ensure it's installed here as well for correctness.
RUN apt-get update && \
    apt-get install -y --no-install-recommends libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

# Copy pre-built wheels and requirements from the builder
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .

# Install Python dependencies from local wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY . .

# Change ownership and switch to non-root user
RUN chown -R app:app /usr/src/app
USER app

EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
