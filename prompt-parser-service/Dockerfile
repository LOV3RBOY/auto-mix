# Dockerfile for services/prompt-parser/

# --- Stage 1: Builder ---
# This stage installs dependencies and downloads the NER model.
FROM python:3.9-slim-buster AS builder

WORKDIR /usr/src/app

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Set a specific cache directory for transformers models inside the build context
ENV TRANSFORMERS_CACHE="/usr/src/app/models_cache"

# Install build tools and pip
RUN apt-get update && apt-get install -y build-essential && \
    pip install --upgrade pip

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install python packages from requirements to make the 'transformers' library available.
RUN pip install --no-cache-dir -r requirements.txt

# Now that packages are installed, download the NER model into the specified cache directory.
# This command runs a short Python script to pre-download the model.
RUN python -c "from transformers import pipeline; pipeline('ner', model='dslim/bert-base-ner')"

# Create wheel files for the much smaller runtime stage.
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

# --- Stage 2: Runtime ---
# This stage creates the final, lean production image.
FROM python:3.9-slim-buster

WORKDIR /usr/src/app

# Create a non-root user and group for security
RUN addgroup --system app && adduser --system --group app

# Set the same cache directory for runtime
ENV TRANSFORMERS_CACHE="/usr/src/app/models_cache"

# Copy installed packages and the model from the builder stage
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
COPY --from=builder ${TRANSFORMERS_CACHE} ${TRANSFORMERS_CACHE}

# Install the packages from the wheel files
RUN pip install --no-cache /wheels/*

# Copy the application source code
COPY . .

# Change ownership of the app directory to the non-root user
RUN chown -R app:app /usr/src/app

# Switch to the non-root user
USER app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]