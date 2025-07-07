# QA Service

A FastAPI-based microservice designed to perform automated quality assurance on generated audio files. This service analyzes an audio file to extract key metrics like tempo, musical key, loudness (LUFS), and clipping.

## Features

- **Tempo Estimation**: Calculates the beats per minute (BPM).
- **Key Estimation**: Determines the musical key (e.g., C major).
- **LUFS Measurement**: Measures the integrated loudness according to the EBU R 128 standard.
- **Clipping Detection**: Identifies if the audio signal has clipped samples.
- **Container-Ready**: Includes a `Dockerfile` for easy deployment.

---

## API Endpoint

### Analyze Audio

Analyzes an uploaded audio file and returns its quality metrics.

- **URL**: `/analyze`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`

#### Parameters

| Name   | Type | Description                        | Required |
|--------|------|------------------------------------|----------|
| `file` | File | The audio file to be analyzed. Supported formats include `.wav`, `.flac`, etc. | Yes      |

#### Example Request

You can use a tool like `curl` to send a request:

curl -X POST "http://localhost:8000/analyze" \
-H "Content-Type: multipart/form-data" \
-F "file=@/path/to/your/audio.wav"
