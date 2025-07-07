import tempfile
import shutil
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import logging

from schemas import AnalysisResult
from analyzer import analyze_audio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Style Analysis Service",
    description="Analyzes audio files to extract musical features like tempo, key, and structure.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_files_dir = os.path.dirname(os.path.abspath(__file__))

@app.get("/", include_in_schema=False)
async def read_index():
    return FileResponse(os.path.join(static_files_dir, 'index.html'))

@app.get("/script.js", include_in_schema=False)
async def read_script():
    return FileResponse(os.path.join(static_files_dir, 'script.js'))


@app.post("/analyze/", response_model=AnalysisResult, tags=["Analysis"])
async def create_analysis(file: UploadFile = File(...)):
    """
    Accepts an audio file, analyzes it, and returns its musical features.

    - **file**: The audio file (e.g., MP3, WAV, FLAC) to be analyzed.
    """
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
        try:
            logger.info(f"Receiving file: {file.filename}")
            shutil.copyfileobj(file.file, tmp_file)
            tmp_file_path = tmp_file.name
        finally:
            file.file.close()

    try:
        logger.info(f"Analyzing file at {tmp_file_path}")
        analysis_result = analyze_audio(tmp_file_path)
        logger.info("Analysis complete.")
        return analysis_result
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred during audio analysis: {str(e)}")
    finally:
        os.remove(tmp_file_path)
        logger.info(f"Cleaned up temporary file: {tmp_file_path}")
