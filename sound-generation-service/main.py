from fastapi import FastAPI, HTTPException
from schemas import GenerationRequest, GenerationResponse
from generator import mock_generate_stems

app = FastAPI(
    title="Sound Generation Service",
    description="A microservice to generate audio stems based on structured prompts.",
    version="1.0.0"
)

@app.post("/generate", response_model=GenerationResponse, tags=["Generation"])
async def generate_track(request: GenerationRequest):
    """
    Accepts a structured prompt and style features to generate audio stems.
    
    This endpoint simulates the generation process, introduces an artificial delay,
    and returns mock file paths for the generated audio stems.
    """
    try:
        result = await mock_generate_stems(request)
        return GenerationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during generation: {str(e)}")

@app.get("/", tags=["Health Check"])
async def read_root():
    """Health check endpoint to confirm the service is running."""
    return {"status": "ok", "message": "Sound Generation Service is running."}
