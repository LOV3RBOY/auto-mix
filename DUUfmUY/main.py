from fastapi import FastAPI, HTTPException
import logging

from schemas import MixingRequest, MixingResponse
from dsp_pipeline import process_mixing_job

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mixing & Mastering Service",
    description="A microservice for mixing and mastering audio stems using Pedalboard.",
    version="1.0.0"
)

@app.post("/process", response_model=MixingResponse, tags=["Mixing"])
async def process_stems(request: MixingRequest):
    if not request.stem_paths:
        raise HTTPException(status_code=400, detail="stem_paths list cannot be empty.")

    try:
        logger.info(f"Received mixing request for {len(request.stem_paths)} stems.")
        output_path = process_mixing_job(request)
        logger.info(f"Successfully processed job. Output at: {output_path}")
        return MixingResponse(
            output_path=output_path,
            message="Mixing and mastering complete. Output saved."
        )
    except Exception as e:
        logger.error(f"An error occurred during mixing process: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

@app.get("/", tags=["Health Check"])
async def read_root():
    return {"status": "ok", "message": "Mixing & Mastering Service is running."}
