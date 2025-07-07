# **Project Blueprint: AI Music Production Assistant**

## 1. Executive Summary

This document outlines the project blueprint for an AI-powered music production assistant. The system's vision is to empower users to generate high-quality, fully produced music tracks from simple natural-language prompts. By referencing existing songs or describing genres and instrumentation, users will receive a ready-to-listen `WAV` file and the corresponding instrument stems.

**Core Objectives:**

*   **Natural Language Interface:** Accept user prompts like "Make a track in the style of Skrillex’s ‘Inhale Exhale’" or "Generate a four-on-the-floor house beat with dubstep-style bass."
*   **High-Fidelity Analysis:** Extract key musical features (tempo, key, structure, timbre, mix profile) from reference tracks.
*   **Multi-Stem Generation:** Synthesize distinct instrumental and vocal stems (drums, bass, synths, etc.) using generative AI models.
*   **Automated Production:** Implement a DSP pipeline for professional mixing and mastering, including leveling, EQ, compression, and loudness normalization.
*   **Production-Ready Output:** Deliver a final mixed track (24-bit/48 kHz WAV) and individual stems for further use.

**Success Metrics:**
*   **Fidelity:** Achieve a spectral similarity score of ≥ 0.85 between the generated track and a reference track's key sections.
*   **Latency:** Complete the end-to-end generation of a 2-minute track in under 5 minutes.
*   **Quality Assurance:** Ensure >95% of generated tracks pass automated QA checks for tempo, key, LUFS targets, and clipping.

---

## 2. System Architecture

### Architectural Decision: Modular Monolith vs. Microservices

A critical initial decision is the choice between a microservices architecture and a modular monolith.

| Criterion | Microservices | Modular Monolith | Analysis & Recommendation |
| :--- | :--- | :--- | :--- |
| **Development Velocity** | Slower initially due to infra overhead (API gateways, service discovery, IPC). | **Faster initially**. Single codebase and deployment target simplifies local development and initial CI/CD. | For a new project, speed is paramount. The Modular Monolith allows the team to focus on feature development over infrastructure. |
| **Operational Complexity**| High. Requires container orchestration (Kubernetes), robust monitoring, and complex deployment strategies from day one. | **Low**. A single application server and database are easier to deploy, monitor, and manage. | The project involves stateful, long-running jobs (audio generation). Managing this across distributed services adds significant complexity that is not justified at this stage. |
| **Scalability** | **Superior**. Individual services (e.g., GPU-intensive Sound Generation) can be scaled independently. | Limited. Scaling requires replicating the entire monolith, which is less resource-efficient. | While microservices offer better scaling, the initial user load will be low. The modular monolith can be scaled vertically or horizontally as a whole, which is sufficient for Phase 1-3. The design will allow for future extraction into microservices if needed. |
| **Fault Isolation** | High. Failure in one service (e.g., mastering) doesn't necessarily bring down the entire system. | Low. An unhandled exception in one module can crash the entire application. | This is a significant advantage for microservices. However, with robust error handling and a job queue, a modular monolith can be made resilient enough for the initial product. |
| **Data Consistency** | Challenging. Requires patterns like Sagas to maintain consistency across service-specific databases. | **Simple**. A single database with ACID transactions ensures strong consistency. | The workflow is a clear, sequential pipeline. A single job-tracking table in one database is far simpler and more reliable than coordinating state across multiple services. |

**Recommendation: Modular Monolith**

We will adopt a **Modular Monolith** architecture. This approach provides the best balance of development speed and operational simplicity for the project's current stage. It enforces clean separation of concerns through well-defined module boundaries within a single codebase, allowing for future evolution into microservices if and when specific components require independent scaling.

### Proposed Architecture Diagram

The system will be designed as a sequential pipeline orchestrated by a central job manager.

> **Frontend (Web UI/CLI)** -> **API Server (Modular Monolith)**
>
> ---
>
> **Inside the Monolith:**
> 1.  **API Controller** receives a request.
> 2.  A new job is created and pushed to the **Job Queue (Redis)**.
> 3.  The **Orchestrator Worker** picks up the job.
> 4.  **Orchestrator** calls **Prompt Parser Module** -> *structured request*.
> 5.  **Orchestrator** calls **Style Analysis Module** (if reference provided) -> *style parameters*.
> 6.  **Orchestrator** calls **Sound Generation Module** (in parallel for each stem) -> *raw audio stems*.
> 7.  **Orchestrator** calls **Mixing & Mastering Module** -> *mixed/mastered track*.
> 8.  **Orchestrator** calls **QA Module** to verify output -> *pass/fail*.
> 9.  **Orchestrator** updates the job status in the **Database (PostgreSQL)** and stores artifacts in **Object Storage (S3)**.

---

## 3. Technology Stack

| Component | Technology | Justification |
| :--- | :--- | :--- |
| **Frontend** | **React (with Vite) + TypeScript** | Provides a robust, type-safe foundation for a minimal but effective web UI. Vite offers an exceptional developer experience with near-instant hot-reloading. |
| **Backend Framework** | **Python 3.11+ with FastAPI** | Python has a mature ecosystem for AI/ML and audio processing. FastAPI delivers high performance, asynchronous support, and automatic OpenAPI documentation, which is ideal for this project. |
| **Database** | **PostgreSQL** | A reliable, feature-rich relational database perfect for storing job metadata, user information, and structured analysis results. |
| **Job Queue & Cache** | **Redis** | High-performance in-memory store, ideal for managing the job queue with a library like Celery and for caching repeated analysis results. |
| **Prompt Parser** | **OpenAI API (gpt-4o-mini) / LangChain** | Utilizing a state-of-the-art LLM with a structured output schema (JSON mode) is the fastest way to implement robust and flexible natural language understanding. |
| **Style Analysis** | **Librosa & Pytorch** | `Librosa` is the industry standard for audio feature extraction (tempo, key, beats). `Pytorch` models can be used for more advanced timbre and structural analysis. |
| **Sound Generation** | **Stability AI MusicGen API Wrapper** | Outsourcing generation to a specialized, high-quality API like MusicGen abstracts away the immense complexity of training and hosting generative audio models. We will build a resilient client wrapper. |
| **Mixing & Mastering** | **Pydub & Pedalboard (by Spotify)** | `Pydub` offers a simple high-level interface for audio manipulation. `Pedalboard` provides access to professional-grade audio effects (EQ, compression, limiting) implemented in C++ for performance, callable directly from Python. |
| **Deployment** | **Docker & Docker Compose** | Containerization ensures consistent environments from development to production. Docker Compose simplifies the local setup of the multi-container application (API server, worker, Postgres, Redis). |
| **Object Storage** | **AWS S3 / MinIO** | Scalable and reliable storage for audio assets (references, stems, final tracks). MinIO can be used for local development. |

---

## 4. Module Breakdown & API Specification

### Core Module Responsibilities

| Module | Responsibilities | Inputs | Outputs |
| :--- | :--- | :--- | :--- |
| **Prompt Parser** | Converts natural language text into a structured JSON object. | `prompt: string` | `StructuredPrompt` (JSON object with keys for `style`, `genre`, `bpm`, `key`, `instruments`, `structure`) |
| **Style Analysis** | Extracts musical features from a provided reference audio file. | `audio_file: bytes` | `StyleParameters` (JSON object with keys for `bpm`, `key`, `loudness_lufs`, `eq_profile`, `structure_markers`) |
| **Sound Generation**| Generates individual audio stems based on the structured prompt. | `stem_description: string`, `duration: int` | `raw_audio_stem: bytes` (WAV format) |
| **Mixing/Mastering**| Combines stems, applies DSP effects, and normalizes the final track. | `stems: list[bytes]`, `mastering_params: StyleParameters` | `mixed_track: bytes`, `mastered_stems: list[bytes]` |
| **Orchestrator** | Manages the end-to-end workflow, sequences module calls, and handles retries. | `job_id: uuid`, `request_data` | `job_status: string`, `artifact_urls: list[string]` |

### Preliminary API Specification (OpenAPI 3.0)

This defines the primary endpoint for initiating a music generation job. The backend will process this asynchronously.

```yaml
openapi: 3.0.1
info:
  title: AI Music Production Assistant API
  version: v1
paths:
  /api/v1/jobs:
    post:
      summary: Create a new music generation job
      operationId: create_music_generation_job
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                prompt:
                  type: string
                  description: "Natural language prompt describing the desired track."
                  example: "A four-on-the-floor house beat with a dubstep-style bass."
                reference_track:
                  type: string
                  format: binary
                  description: "Optional reference audio file (e.g., WAV, MP3) for style analysis."
      responses:
        '202':
          description: Job accepted for processing.
          content:
            application/json:
              schema:
                type: object
                properties:
                  job_id:
                    type: string
                    format: uuid
                    description: "The unique identifier for the created job."
                  status_url:
                    type: string
                    format: uri
                    description: "URL to poll for job status."
        '400':
          description: Bad request (e.g., missing prompt).

  /api/v1/jobs/{job_id}:
    get:
      summary: Get job status and results
      operationId: get_job_status
      parameters:
        - name: job_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: "Current status and results of the job."
          content:
            application/json:
              schema:
                type: object
                properties:
                  job_id:
                    type: string
                    format: uuid
                  status:
                    type: string
                    enum: [queued, processing, failed, completed]
                  progress:
                    type: integer
                    example: 75
                  results:
                    type: object
                    properties:
                      mixed_track_url:
                        type: string
                        format: uri
                      stems:
                        type: array
                        items:
                          type: object
                          properties:
                            instrument:
                              type: string
                              example: "drums"
                            url:
                              type: string
                              format: uri
        '404':
          description: Job not found.
```

---

## 5. Phased Development Roadmap

| Phase | Title | Key Deliverables |
| :--- | :--- | :--- |
| **Phase 1** | **Foundational Setup & Core AI Modules** | - Project setup with Docker, FastAPI, PostgreSQL, and Redis.<br>- **Prompt Parser Module**: Integrated with OpenAI API.<br>- **Sound Generation Module**: Functional wrapper around the MusicGen API.<br>- **Mixing & Mastering Module**: Basic stem combination and loudness normalization (`Pedalboard`). |
| **Phase 2** | **Backend Orchestration & Integration** | - **Orchestrator Module**: Implement Celery worker to manage the job lifecycle.<br>- **Style Analysis Module**: Implement `librosa` for tempo and key detection.<br>- End-to-end headless flow: A command-line script can trigger a job that executes all modules in sequence.<br>- Initial database schema for tracking jobs. |
| **Phase 3**| **Frontend & End-to-End Workflow** | - Minimal React frontend for submitting prompts and uploading files.<br>- Integration of the frontend with the FastAPI backend endpoints.<br>- Polling mechanism on the frontend to display job status.<br>- Display and allow download of final audio artifacts. |
| **Phase 4** | **Productionization & Hardening** | - **CI/CD Pipeline** (GitHub Actions): Automated linting, testing, and Docker image builds.<br>- Comprehensive logging and monitoring (e.g., Prometheus, Grafana).<br>- **QA Module**: Automated checks for tempo, key, and LUFS in the orchestration flow.<br>- Error handling and retry logic within the orchestrator. |

---

## 6. Testing and QA Strategy

A multi-layered approach will ensure system reliability and output quality.

1.  **Unit Testing (`pytest`)**:
    *   **Prompt Parser**: Test with various prompts (simple, complex, malformed) and assert the correctness of the structured JSON output.
    *   **Style Analysis**: Use known audio files with fixed tempos/keys and assert that `librosa` extracts the correct values within a small tolerance.
    *   **DSP Utilities**: Test mixing functions with silent/mono/stereo inputs. Test mastering chain functions to ensure they apply effects correctly (e.g., a limiter prevents clipping).

2.  **Integration Testing**:
    *   **API <> Orchestrator**: Test the full API request-to-job-queue pipeline. Verify that a `POST` request to `/api/v1/jobs` correctly creates a job in Redis with the right parameters.
    *   **Module Chain**: Create test pipelines that run modules sequentially on mock data. For example, verify that the `bpm` from the Style Analysis output is correctly passed to the Sound Generation module's prompt.

3.  **End-to-End (E2E) Quality Assurance**:
    *   This is a critical, automated step at the end of the orchestration pipeline. Before a job is marked as "completed," the final WAV file will be analyzed.
    *   **QA Checklist:**
        *   **Tempo Check**: Analyze the generated track's tempo. *Pass if within ±2 BPM of the target.*
        *   **Key Check**: Analyze the key. *Pass if it matches the target key.*
        *   **Loudness Check**: Measure integrated loudness. *Pass if within ±0.5 LU of the target (e.g., -14 LUFS).*
        *   **Clipping Check**: Scan for digital clipping. *Pass if true peak is ≤ -1.0 dBFS.*
    *   **Failure/Retry Logic**: If any QA check fails, the job is marked as "failed" with a reason. The orchestrator will trigger a retry (up to 2 times), potentially with modified generation parameters (e.g., adding "in D minor" to the prompt if the key was wrong).