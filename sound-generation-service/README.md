# Sound Generation Service

This microservice is a core component of the AI Music Production Assistant. It is responsible for generating audio stems (e.g., drums, bass, synths) based on a structured prompt from the `Prompt Parser Service` and style features from the `Style Analysis Service`.

> This service is part of the AI Music Production Assistant. For global project information, see the [root README.md](../../README.md).

This implementation features a **mock generation engine**. It simulates the time-consuming process of AI audio synthesis and returns a list of mock file paths for the generated stems. This allows for testing the end-to-end workflow of the assistant without needing access to expensive GPU hardware or paid APIs.

---

## Architecture

-   **Framework**: FastAPI
-   **Language**: Python 3.9+
-   **Data Validation**: Pydantic
-   **Deployment**: Docker

The service exposes a single primary endpoint, `/generate`, which asynchronously processes generation requests.

---

## API

### `POST /generate`

Accepts a structured prompt and optional style features to generate audio stems.

-   **Request Body:**
    ```json
    {
      "prompt_spec": {
        "tempo": 120,
        "key": "A Minor",
        "genre": "techno",
        "instruments": ["drums", "bass", "synth lead"],
        "style_references": [],
        "mood": "dark"
      },
      "style_features": {
        "tempo": 120.5,
        "key": "A Minor",
        "segments": []
      }
    }
