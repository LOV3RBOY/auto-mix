# Style Analysis Service

This is a microservice designed for the AI Music Production Assistant. Its primary function is to analyze an audio file and extract core musical features: tempo (BPM), musical key, and structural segmentation.

> This service is part of the AI Music Production Assistant. For global project information, see the [root README.md](../../README.md).

The service is built with Python, FastAPI, and `librosa`.

---

## Features

-   **Tempo Detection**: Estimates the global tempo of the track in Beats Per Minute (BPM).
-   **Key Estimation**: Determines the most likely musical key (e.g., "C# Minor").
-   **Structural Segmentation**: Divides the track into distinct sections (e.g., "Part A", "Part B").

---

## Technology Stack

-   **Backend**: Python 3.9+
-   **API Framework**: FastAPI
-   **Audio Analysis**: Librosa
-   **Deployment**: Docker

---

## Web Interface

For easy testing, this service includes a simple HTML/JS interface. If you run the service locally (not in Docker), you can access it at `http://127.0.0.1:8000/`.

## API

### `POST /analyze/`

Accepts an audio file upload and returns its musical features.

-   **Request**: `multipart/form-data` with a `file` field containing the audio file.
-   **Success Response (200 OK):**
    ```json
    {
        "tempo": 174.05,
        "key": "F# Minor",
        "segments": [
            { "start_time": 0.0, "end_time": 15.2, "label": "Part A" },
            { "start_time": 15.2, "end_time": 30.8, "label": "Part B" }
        ]
    }
