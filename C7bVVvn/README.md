# AI Music Production Assistant

Welcome to the AI Music Production Assistant, a full-stack application designed to generate complete music tracks from natural language prompts. This project leverages a microservice architecture to handle distinct stages of the music creation process, from prompt analysis to final mastering.

---

## 1. System Architecture

The application is built around a central **Job Orchestrator** that manages a workflow across several specialized microservices. A request from a client (e.g., the CLI) triggers a series of asynchronous tasks handled by a Celery worker.

### Architectural Flow

1.  **Client Request**: A user submits a prompt via the **CLI Client**.
2.  **Job Creation**: The request hits the **Job Orchestrator**, which creates a unique job ID and dispatches a task pipeline to the **Celery Queue** (backed by Redis).
3.  **Prompt Parsing**: The first worker task calls the **Prompt Parser Service** to convert the natural language prompt into a structured JSON object.
4.  **Style Analysis (Optional)**: If a reference file is provided, the **Style Analysis Service** is called to extract features like tempo and key.
5.  **Sound Generation**: The structured data is sent to the **Sound Generation Service**, which creates mock audio stems.
6.  **Mixing & Mastering**: The stem paths are passed to the **Mixing & Mastering Service**, which mixes them, applies a DSP chain, and saves a final WAV file to a shared volume.
7.  **Job Completion**: The orchestrator marks the job as complete, and the client can retrieve the path to the final track.

---

## 2. Prerequisites

-   [Docker](https://www.docker.com/get-started)
-   [Docker Compose](https://docs.docker.com/compose/install/)
-   [Python 3.8+](https://www.python.org/downloads/)

---

## 3. How to Run the System

1.  **Start the Services**:
    From the root directory of the project, run Docker Compose. This will build the images for each service and start the containers.

    ```bash
    docker-compose up --build -d
