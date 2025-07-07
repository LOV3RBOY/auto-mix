import io
import numpy as np
import librosa
import soundfile as sf
import pyloudnorm as pyln
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

# --- FastAPI App Initialization ---
app = FastAPI(
    title="QA Service",
    description="A microservice to perform automated quality assurance on audio files.",
    version="1.0.0",
)

# --- Pydantic Models for Response ---
class AnalysisDetails(BaseModel):
    tempo: float
    key: str
    lufs: float
    clipping: bool

class AnalysisResponse(BaseModel):
    status: str
    details: AnalysisDetails

# --- Helper Functions for Audio Analysis ---

def estimate_key(y: np.ndarray, sr: int) -> str:
    """Estimates the musical key of an audio signal using Krumhansl-Schmuckler profiles."""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

    chromagram = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_vector = np.sum(chromagram, axis=1)
    
    if np.sum(chroma_vector) > 0:
        chroma_vector /= np.sum(chroma_vector)

    correlations = []
    for i in range(12):
        major_corr = np.corrcoef(chroma_vector, np.roll(major_profile, i))[0, 1]
        correlations.append((major_corr, f"{notes[i]} major"))
        
        minor_corr = np.corrcoef(chroma_vector, np.roll(minor_profile, i))[0, 1]
        correlations.append((minor_corr, f"{notes[i]} minor"))
        
    if not correlations:
        return "N/A"

    best_corr, best_key = max(correlations, key=lambda item: item[0] if not np.isnan(item[0]) else -1)
    
    return best_key if not np.isnan(best_corr) else "N/A"

def analyze_audio_data(data: np.ndarray, sr: int) -> Dict[str, Any]:
    """Performs all audio analyses and returns a dictionary of results."""
    
    y_mono = np.mean(data, axis=1) if data.ndim > 1 else data

    # 1. Tempo Estimation
    tempo_values = librosa.beat.tempo(y=y_mono, sr=sr)
    tempo = tempo_values[0] if tempo_values.size > 0 else 0.0

    # 2. Key Estimation
    key = estimate_key(y=y_mono, sr=sr)

    # 3. LUFS Measurement
    meter = pyln.Meter(sr)
    lufs = meter.integrated_loudness(data)
    
    # 4. Clipping Detection
    if np.issubdtype(data.dtype, np.floating):
        threshold = 0.999
    else:
        threshold = np.iinfo(data.dtype).max * 0.999
    
    is_clipping = np.any(np.abs(data) >= threshold)

    return {
        "tempo": float(tempo),
        "key": key,
        "lufs": float(lufs) if lufs > -np.inf else -99.0,
        "clipping": bool(is_clipping),
    }

# --- API Endpoint ---
@app.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def create_analysis(file: UploadFile = File(...)):
    """
    Analyzes an uploaded audio file for tempo, key, LUFS, and clipping.

    - **file**: The audio file to analyze (e.g., .wav, .mp3, .flac).
    """
    if not file.content_type or not (file.content_type.startswith("audio/") or file.content_type == "application/octet-stream"):
        raise HTTPException(status_code=400, detail=f"Invalid file Content-Type: {file.content_type}. Please upload an audio file.")

    try:
        file_content = await file.read()
        file_buffer = io.BytesIO(file_content)

        data, samplerate = sf.read(file_buffer, dtype='float32', always_2d=True)
        data = data.T # Transpose to get (channels, samples) for librosa/pyloudnorm

    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not read audio file. It may be corrupted or in an unsupported format. Error: {str(e)}")
        
    try:
        analysis_results = analyze_audio_data(data, samplerate)
        
        status = "pass" if not analysis_results["clipping"] else "fail"
        
        return {"status": status, "details": analysis_results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during audio analysis: {str(e)}")

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "QA Service is running. POST to /analyze to check an audio file."}
