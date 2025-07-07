# Job Orchestrator Service

This service is the central nervous system of the AI Music Production Assistant. It is responsible for taking a user's request, orchestrating a complex, multi-step workflow across various specialized microservices, and tracking the job's progress from start to finish.

> This service is part of the AI Music Production Assistant. For global project information, see the [root README.md](../../README.md).

---

## 1. Architecture

The orchestrator sits at the center of the music generation ecosystem. When a user submits a prompt, the orchestrator translates this into a series of asynchronous tasks.

1.  **API Layer (FastAPI)**: Exposes endpoints to create a job and check its status. It receives the user's prompt, creates a unique job ID, and immediately dispatches the job to the Celery queue. It returns the job ID to the client, allowing for status polling.

2.  **Task Queue (Celery & Redis)**: Celery manages the asynchronous execution of the workflow. Redis serves as the message broker (passing tasks from the API to workers) and the results backend (storing task states and return values).

3.  **Workflow Pipeline**: The core logic is defined as a Celery `chain`, ensuring tasks execute in the correct order. The sequence is:
    1.  **Prompt Parser**: The initial text prompt is sent to the `Prompt Parser Service`.
    2.  **Style Analysis (Optional)**: If a reference track URL is provided, it's sent to the `Style Analysis Service`.
    3.  **Sound Generation**: The structured data from the previous steps is sent to the `Sound Generation Service` to create audio stems.
    4.  **Mixing & Mastering**: The generated stems are sent to the `Mixing & Mastering Service` to produce the final track.
    5.  **Finalization**: The job status is updated, and the final artifact URL is stored.

4.  **State Management**: The service maintains the state of each job (e.g., `PENDING`, `PROCESSING`, `SUCCESS`, `FAILURE`) in a simple in-memory dictionary. In a production system, this would be replaced by a persistent database like PostgreSQL.

---

## 2. API Endpoints

### `POST /create-track`

Initiates a new music generation job.

-   **Request Body**:
    ```json
    {
      "prompt": "A chill lo-fi hip hop beat with a smooth piano melody, 100 bpm.",
      "reference_track_url": "https://example.com/audio/reference.wav"
    }
