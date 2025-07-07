# Mixing & Mastering Microservice

This microservice is a component of the larger AI Music Production Assistant. Its purpose is to take a collection of individual audio stems (e.g., drums, bass, synths), mix them together, apply a professional mastering chain, and produce a single, high-quality WAV file ready for listening.

> This service is part of the AI Music Production Assistant. For global project information, see the [root README.md](../../README.md).

The service is built with Python, [FastAPI](https://fastapi.tiangolo.com/), and Spotify's [Pedalboard](https://github.com/spotify/pedalboard) library for all Digital Signal Processing (DSP) tasks.

This implementation uses **mock logic**. It does not require real audio files as input. Instead, it simulates the process by generating silent audio internally, allowing for end-to-end testing of the API and DSP pipeline without actual sound generation dependencies.

---

## Features

-   **FastAPI Backend**: A modern, high-performance Python web framework.
-   **Pydantic Models**: Ensures robust data validation for API requests and responses.
-   **DSP Pipeline**: A mock audio processing chain including:
    -   Mixing multiple stems.
    -   Applying effects: Compressor, High-pass Filter, and Equalizer.
    -   Mastering to a target loudness of **-14 LUFS**.
-   **High-Quality Output**: Saves the final mix as a **24-bit, 48kHz WAV** file.
-   **Containerized**: Fully containerized with Docker for easy deployment and scalability.

---

## API

### `POST /process`

Takes a list of file paths to audio stems and returns the path to the final processed file.

-   **Request Body**:
    ```json
    {
      "stem_paths": [
        "/stems/job_xyz_drums.wav",
        "/stems/job_xyz_bass.wav"
      ]
    }
