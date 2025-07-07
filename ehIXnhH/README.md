# Sound Generation Service

This microservice is a core component of the AI Music Production Assistant. It is responsible for generating audio stems (e.g., drums, bass, synths) based on a structured prompt from the `Prompt Parser Service` and style features from the `Style Analysis Service`.

This implementation features a **mock generation engine**. It simulates the time-consuming process of AI audio synthesis and returns a list of mock file paths for the generated stems. This allows for testing the end-to-end workflow of the assistant without needing access to expensive GPU hardware or paid APIs.

---

## Architecture

-   **Framework**: FastAPI
-   **Language**: Python 3.9+
-   **Data Validation**: Pydantic
-   **Deployment**: Docker

The service exposes a single primary endpoint, `/generate`, which asynchronously processes generation requests.

---

## How to Run

The service is containerized using Docker for easy setup and deployment.

### Prerequisites

-   [Docker](https://www.docker.com/get-started) installed and running on your machine.

### 1. Build the Docker Image

From the root directory of this service, run the following command to build the image:

docker build -t sound-generation-service .
