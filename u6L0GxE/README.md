# Style Analysis Service

This is a microservice designed for the AI Music Production Assistant. Its primary function is to analyze an audio file and extract core musical features: tempo (BPM), musical key, and structural segmentation.

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

## Prerequisites

-   [Docker](https://www.docker.com/get-started) must be installed on your system.
-   For local development outside of Docker, you will need to install `libsndfile`.
    -   On Debian/Ubuntu: `sudo apt-get install libsndfile1`
    -   On macOS (with Homebrew): `brew install libsndfile`

---

## Getting Started

You can run this service easily using the provided Dockerfile.

### 1. Build the Docker Image

Open your terminal in the project's root directory and run:

docker build -t style-analysis-service .
