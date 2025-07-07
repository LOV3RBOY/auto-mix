# AI Music Production Assistant Documentation

---

## Root: `README.md`

# AI Music Production Assistant

Welcome to the AI Music Production Assistant, a full-stack, production-ready application designed to generate complete music tracks from natural language prompts. This project leverages a robust microservice architecture to handle distinct stages of the music creation process, from prompt analysis to automated quality assurance and final mastering.

---

## **1. System Architecture**

The application is built around a central **Job Orchestrator** that manages a workflow across several specialized microservices. A **React UI** serves as the user's entry point, communicating with the orchestrator via a REST API. The entire system is containerized with Docker for easy deployment and scalability.

### **Architectural Components**

| Component                 | Technology        | Role                                                                                             |
| ------------------------- | ----------------- | ------------------------------------------------------------------------------------------------ |
| **Frontend UI**           | React             | Provides a web interface for users to submit prompts and view results.                           |
| **Job Orchestrator**      | FastAPI, Celery   | The central API and workflow engine. Manages the job lifecycle and task chains.                  |
| **Prompt Parser**         | FastAPI, Hugging Face | Parses natural language prompts into structured data using an NER transformer model.           |
| **Style Analysis**        | FastAPI, Librosa  | (Optional) Analyzes reference audio to extract features like tempo and key.                       |
| **Sound Generation**      | FastAPI, Stability AI | Generates audio from structured prompts by calling the Stability AI Stable Audio API.               |
| **Mixing & Mastering**    | FastAPI           | Combines generated audio stems into a single, mastered track.                                    |
| **Quality Assurance (QA)**| FastAPI, Librosa  | Analyzes the final track for technical quality (LUFS, clipping, etc.) and triggers retries.      |
| **Job & Task Broker**     | Redis             | Message broker for Celery tasks, enabling asynchronous processing.                                 |
| **Persistent Storage**    | PostgreSQL        | Stores all job information, including status, retries, and final results.                      |

### **High-Level Data Flow**

```
+-----------+       +------------------------+       +--------------------+
| React UI  |------>| Job Orchestrator API   |------>|   PostgreSQL DB    |
+-----------+       | (FastAPI)              |       | (Stores Job State) |
                    +------------------------+       +--------------------+
                              |
                              | Dispatches Job
                              v
+------------------------+  +------------------------+
|    Redis Broker        |<--|    Celery Worker(s)    |
| (Task Queue)           |-->| (Executes Pipeline)    |
+------------------------+  +------------------------+
                              |
                              | Executes Task Chain
                              v
[ 1. Prompt Parser ] -> [ 2. Sound Generation ] -> [ 3. Mixing/Mastering ] -> [ 4. QA Service ]
        ^                                                                           |
        |                                                                           | (On Failure)
        +-----------------------------------<---[ 5. Retry Logic ]------------------+
```

---

## **2. Quick Start**

This project is fully containerized. With Docker and Docker Compose installed, you can launch the entire stack with a single command from the project root directory.

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/ai-music-production-assistant.git
    cd ai-music-production-assistant
    ```

2.  **Configure API Keys:**
    Navigate to the `services/sound-generation-service/` directory and create a `.env` file with your Stability AI API key:
    ```
    STABILITY_AI_API_KEY="your_stability_ai_key_here"
    ```

3.  **Build and Run Services:**
    From the root directory, run:
    ```sh
    docker-compose up --build
    ```
    This command builds the images for all microservices and starts the containers.

4.  **Access the Application:**
    -   **Frontend UI**: `http://localhost:3000`
    -   **Orchestrator API**: `http://localhost:8000/docs`

---

## **3. End-to-End Workflow**

The system follows a sophisticated, resilient workflow to process each user request.

1.  **Job Initiation**: A user enters a prompt into the React UI and clicks "Generate." The UI sends a `POST` request to the Job Orchestrator's `/create-track` endpoint.

2.  **Job Persistence & Queuing**: The Orchestrator creates a new job entry in the PostgreSQL database with a unique `job_id` and `PENDING` status. It then dispatches the job to a Celery task queue, using Redis as the message broker. The `job_id` is returned to the UI.

3.  **Asynchronous Execution**: A Celery worker picks up the job and begins executing a predefined chain of tasks:
    -   **Prompt Parsing**: The text prompt is sent to the `Prompt Parser` service, which uses an NER model to extract entities like genre, instruments, and mood.
    -   **Sound Generation**: The structured prompt is sent to the `Sound Generation` service, which calls the Stability AI API to generate the raw audio.
    -   **Mixing & Mastering**: The generated audio is processed by the `Mixing & Mastering` service to produce a final, polished track.

4.  **Quality Assurance Check**: The final track is sent to the `QA Service` for automated analysis. It checks metrics like loudness (LUFS), clipping, tempo, and key against desired targets.

5.  **Retry & Finalization Loop**:
    -   **If QA passes**: The job status in PostgreSQL is updated to `SUCCESS`, and the final track URL is saved.
    -   **If QA fails**: The Orchestrator checks the job's `retry_count`. If it's below the maximum limit, it increments the count, appends corrective instructions to the original prompt (e.g., `--target_lufs -14`), and re-launches the entire workflow from the beginning.
    -   **If max retries are reached**: The job status is marked as `FAILED_QA`.

6.  **Status Polling**: Throughout this process, the React UI periodically polls the Orchestrator's `/jobs/{job_id}` endpoint to get the latest status, which is reflected live to the user.

---

## **services/frontend/README.md**

# Frontend Service (React UI)

This service provides the primary user interface for the AI Music Production Assistant. It is a modern, responsive web application built with React.

## **1. Role in the System**

The frontend's main responsibilities are:
-   To provide a clean and intuitive interface for users to submit music generation prompts.
-   To communicate with the backend **Job Orchestrator** API to create new jobs.
-   To continuously poll for the status of active jobs and display real-time progress.
-   To present the final results, including download links for the generated track and its stems.

## **2. Running in a Development Environment**

To run the frontend service locally for development:

1.  **Navigate to the service directory:**
    ```sh
    cd services/frontend
    ```

2.  **Install dependencies:**
    ```sh
    npm install
    ```

3.  **Start the development server:**
    ```sh
    npm start
    ```
    This will launch the application, typically on `http://localhost:3000`, with hot-reloading enabled.

## **3. Backend Communication**

The React application is a pure client-side UI. It interacts with the backend exclusively through HTTP requests to the **Job Orchestrator** service API, which must be running and accessible.

-   **Job Creation**: Sends a `POST` request to `/create-track` with the user's prompt.
-   **Status Updates**: Sends `GET` requests to `/jobs/{job_id}` to poll for the status and result of a job.

The API endpoint is configured in the application's source code (e.g., in `js/app.js`).

---

## **services/prompt-parser/README.md**

# Prompt Parser Service

This microservice is responsible for parsing natural language music prompts into a structured JSON format that downstream services can utilize.

## **1. Core Functionality**

The service exposes a single API endpoint that accepts a text prompt and returns a structured object containing identified musical attributes.

### **Technology Upgrade: From Regex to NER**

This service now utilizes a sophisticated **Named Entity Recognition (NER)** model (`dslim/bert-base-ner` from Hugging Face) to identify musical entities. This transformer-based approach provides significantly higher accuracy and flexibility compared to the previous regex-only logic, allowing for a more nuanced understanding of user prompts.

It can robustly extract:
-   **Tempo**: e.g., "140 bpm"
-   **Key**: e.g., "in C# minor"
-   **Genre**: e.g., "house", "drum and bass"
-   **Instruments**: e.g., "piano", "reese bass"
-   **Moods**: e.g., "energetic", "melancholic"
-   **Style References**: e.g., "in the style of Daft Punk"

## **2. API Endpoint**

### Parse Prompt

-   **URL**: `/api/v1/parse`
-   **Method**: `POST`
-   **Request Body**:
    ```json
    {
      "prompt": "A high-energy drum and bass track at 174 bpm in the style of Pendulum, with a heavy reese bass"
    }
    ```
-   **Success Response (200 OK)**:
    ```json
    {
      "tempo": 174,
      "key": null,
      "genre": "drum and bass",
      "instruments": [
        "bass"
      ],
      "style_references": [
        "Pendulum"
      ],
      "mood": "high-energy"
    }
    ```

---

## **services/sound-generation/README.md**

# Sound Generation Service

This microservice is a critical component of the AI Music Production Assistant. It is responsible for generating audio from structured prompts by integrating directly with **Stability AI's Stable Audio API**.

This service provides a production-ready, robust interface for audio generation, replacing the previous mock engine.

## **1. Architecture**

-   **Framework**: FastAPI
-   **API Integration**: Directly calls the Stability AI REST API.
-   **Configuration**: Manages API keys and settings via environment variables.
-   **Deployment**: Fully containerized with Docker for seamless deployment.

## **2. Configuration (Crucial)**

To use this service, you **must** provide your Stability AI API key.

1.  Create a file named `.env` in the root directory of *this service* (`services/sound-generation/`).
2.  Add your API key to the `.env` file like so:
    ```
    STABILITY_AI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ```
> **Warning**: The service will raise an error and fail to process requests if the `STABILITY_AI_API_KEY` is not set.

## **3. API Endpoint**

### Generate Sound

-   **URL**: `/generate`
-   **Method**: `POST`
-   **Request Body**: A JSON object containing the prompt and desired duration.
    ```json
    {
      "prompt": "An epic cinematic soundtrack with a choir",
      "duration_seconds": 45
    }
    ```
-   **Success Response (200 OK)**:
    ```json
    {
      "file_path": "generated_audio/c7a1a2f0-9b4f-4d4e-8f5b-1e2a3c4d5e6f.wav",
      "prompt": "An epic cinematic soundtrack with a choir",
      "duration_seconds": 45
    }
    ```

---

## **services/job-orchestrator/README.md**

# Job Orchestrator Service

This service is the central nervous system of the AI Music Production Assistant. It is responsible for taking a user's request, orchestrating a complex, multi-step workflow across various microservices, and tracking the job's state persistently.

## **1. Architecture**

The orchestrator combines a synchronous API with an asynchronous task execution system.

1.  **API Layer (FastAPI)**: Exposes endpoints like `/create-track` and `/jobs/{job_id}`. It handles initial request validation and job creation.

2.  **Persistent State (PostgreSQL)**: Job state, prompts, results, and retry counts are persisted in a **PostgreSQL** database. This replaces the previous volatile in-memory storage, ensuring no data is lost on service restart.

3.  **Task Queue (Celery & Redis)**: It uses Celery for managing the asynchronous execution of the generation workflow. Redis serves as the message broker.

### **Workflow Pipeline with QA**

The core logic is defined as a Celery `chain`, ensuring tasks execute in the correct order. The robust pipeline now includes an automated quality check:

1.  **Prompt Parsing**: The text prompt is sent to the `Prompt Parser Service`.
2.  **Sound Generation**: The structured data is sent to the `Sound Generation Service`.
3.  **Mixing & Mastering**: The generated audio is sent to the `Mixing & Mastering Service`.
4.  **Quality Assurance Check**: The final track is sent to the `QA Service` for analysis.

### **Automated Retry Logic**

A key feature of the orchestrator is its ability to handle QA failures gracefully.
-   If the `QA Service` reports that a track has failed (e.g., it's clipping or has the wrong loudness), the orchestrator automatically triggers a retry.
-   It increments a `retry_count` in the database and re-dispatches the entire workflow.
-   This process repeats up to a configured maximum number of retries, enhancing the reliability and quality of the final output.

## **2. API Endpoints**

### Create a new Track

-   **Endpoint**: `POST /create-track`
-   **Description**: Initiates a new music generation job. The job is queued immediately, and the `job_id` is returned.

### Get Job Status

-   **Endpoint**: `GET /jobs/{job_id}`
-   **Description**: Retrieves the current status and result of a specific job from the PostgreSQL database.

---

## **services/qa-service/README.md**

# Quality Assurance (QA) Service

A FastAPI-based microservice designed to perform automated quality assurance on generated audio files. This service analyzes an audio file to extract key technical metrics and determines if it meets production standards.

## **1. Purpose**

The QA Service acts as an automated gatekeeper in the music generation pipeline. By analyzing the final output from the Mixing & Mastering service, it ensures a consistent level of technical quality and provides the pass/fail signal that drives the Orchestrator's retry logic.

## **2. Features**

-   **Tempo Estimation**: Calculates the beats per minute (BPM).
-   **Key Estimation**: Determines the musical key (e.g., C Major).
-   **Loudness Measurement**: Measures the integrated loudness in LUFS (Loudness Units Full Scale) according to the EBU R 128 standard.
-   **Clipping Detection**: Identifies if the audio signal contains clipped (distorted) samples.
-   **Container-Ready**: Includes a `Dockerfile` for easy deployment.

## **3. API Endpoint**

### Analyze Audio

Analyzes an uploaded audio file and returns its quality metrics and a pass/fail status.

-   **URL**: `/analyze`
-   **Method**: `POST`
-   **Content-Type**: `multipart/form-data`

#### **Parameters**

| Name   | Type | Description                        | Required |
|--------|------|------------------------------------|----------|
| `file` | File | The audio file to be analyzed. Supported formats include `.wav`, `.flac`. | Yes      |

#### **Example Request**
```sh
curl -X POST "http://localhost:8006/analyze" \
-H "Content-Type: multipart/form-data" \
-F "file=@/path/to/your/audio.wav"
```

#### **Example Response (Fail)**
```json
{
  "status": "fail",
  "details": {
    "tempo": 120.0,
    "key": "A Minor",
    "lufs": -8.5,
    "clipping": true
  }
}
```