import uuid
from typing import Dict, Any, Optional

import httpx
from celery import chain
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field

from celery_worker import celery_app
from config import settings

# --- FastAPI App Setup ---
app = FastAPI(
    title="Job Orchestrator Service",
    description="Orchestrates the AI music generation pipeline.",
    version="1.0.0",
)

# --- In-Memory Job Store ---
# In a production environment, this would be a persistent database like PostgreSQL or Redis.
JOB_STATUS: Dict[str, Dict[str, Any]] = {}

# --- Pydantic Models ---
class TrackRequest(BaseModel):
    prompt: str = Field(..., description="The natural language prompt for the music.")
    reference_track_url: Optional[str] = Field(None, description="A URL to an audio file for style analysis.")

class JobResponse(BaseModel):
    job_id: str
    status: str
    details: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[Any] = None

# --- Helper Functions ---
def update_job_status(job_id: str, status: str, result: Optional[Any] = None):
    """Updates the status and result of a job in the in-memory store."""
    if job_id in JOB_STATUS:
        JOB_STATUS[job_id]['status'] = status
        if result:
            JOB_STATUS[job_id]['result'] = result
    print(f"Job {job_id} updated -> Status: {status}, Result: {result}")


# --- Celery Tasks ---
@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def run_prompt_parser(self, job_id: str, prompt: str):
    """Task to call the Prompt Parser service."""
    update_job_status(job_id, "PROCESSING", {"step": "Parsing Prompt"})
    try:
        with httpx.Client() as client:
            response = client.post(settings.PROMPT_PARSER_URL, json={"prompt": prompt}, timeout=30)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as exc:
        raise self.retry(exc=exc)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def run_style_analysis(self, previous_result: dict, job_id: str, reference_track_url: str):
    """Task to call the Style Analysis service. Placeholder for now."""
    # In a real app, this task would download the file from the URL
    # and send the binary data to the style analysis service.
    update_job_status(job_id, "PROCESSING", {"step": "Analyzing Style"})
    print(f"[{job_id}] Style analysis would run for: {reference_track_url}")
    # For now, we return a mock result and merge it with the prompt result
    mock_style_result = {"tempo": 120.5, "key": "C# Minor", "segments": []}
    return {"prompt_spec": previous_result, "style_features": mock_style_result}

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_sound_generation(self, previous_result: dict, job_id: str):
    """Task to call the Sound Generation service."""
    update_job_status(job_id, "PROCESSING", {"step": "Generating Sound"})
    
    # If style analysis didn't run, structure the payload correctly.
    payload = previous_result if "prompt_spec" in previous_result else {"prompt_spec": previous_result}
    
    try:
        with httpx.Client() as client:
            response = client.post(settings.SOUND_GENERATION_URL, json=payload, timeout=300)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as exc:
        raise self.retry(exc=exc)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def run_mixing_mastering(self, previous_result: dict, job_id: str):
    """Task to call the Mixing & Mastering service."""
    update_job_status(job_id, "PROCESSING", {"step": "Mixing and Mastering"})
    stem_paths = list(previous_result.get("stems", {}).values())
    if not stem_paths:
        raise ValueError("No stems found from sound generation step.")
        
    try:
        with httpx.Client() as client:
            payload = {"stem_paths": stem_paths}
            response = client.post(settings.MIXING_MASTERING_URL, json=payload, timeout=180)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as exc:
        raise self.retry(exc=exc)

@celery_app.task
def finalize_job(previous_result: dict, job_id: str):
    """Final task to mark the job as successful."""
    final_track_url = previous_result.get("output_path")
    update_job_status(job_id, "SUCCESS", {"final_track_url": final_track_url})

@celery_app.task
def handle_error(task_id, exc, traceback, job_id: str):
    """Task to handle errors in the workflow."""
    print(f"Error in task {task_id} for job {job_id}: {exc}")
    update_job_status(job_id, "FAILURE", {"error": str(exc)})


# --- FastAPI Endpoints ---
@app.post("/create-track", response_model=JobResponse, status_code=202)
async def create_track(request: TrackRequest):
    """
    Accepts a user prompt and optional reference track to start a music generation job.
    """
    job_id = str(uuid.uuid4())
    JOB_STATUS[job_id] = {"status": "PENDING", "result": None}

    # Define the core workflow tasks
    prompt_task = run_prompt_parser.s(job_id=job_id, prompt=request.prompt)
    sound_gen_task = run_sound_generation.s(job_id=job_id)
    mixing_task = run_mixing_mastering.s(job_id=job_id)
    final_task = finalize_job.s(job_id=job_id)

    workflow_tasks = [prompt_task]

    # Add style analysis to the chain if a reference URL is provided
    if request.reference_track_url:
        style_task = run_style_analysis.s(job_id=job_id, reference_track_url=request.reference_track_url)
        workflow_tasks.append(style_task)

    workflow_tasks.extend([sound_gen_task, mixing_task, final_task])

    # Create the final Celery chain
    workflow_chain = chain(*workflow_tasks)
    workflow_chain.link_error(handle_error.s(job_id=job_id))

    # Dispatch the workflow
    workflow_chain.apply_async()

    return JobResponse(job_id=job_id, status="PENDING", details="Job has been queued.")


@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Retrieves the status and result of a previously created job.
    """
    job = JOB_STATUS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(job_id=job_id, status=job["status"], result=job["result"])

@app.get("/")
async def root():
    return {"message": "Job Orchestrator Service is running."}
